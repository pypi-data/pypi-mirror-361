# Use hydra config to run the script
# python examples/scannet.py train.batch_size=12 model=sparse_convunet model.in_channels=3
# python examples/scannet.py train.batch_size=12 model=mink_unet
# python examples/scannet.py train.batch_size=4 model=point_transformer_v3 model.out_type=segmentation model.out_channels=20 use_wandb=false train.batch_size=2 test.batch_size=2
import os
import random
import time
import warnings
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import hydra
import lightning.pytorch as pl
import numpy as np
import torch
import torch.distributed as dist
import torch.nn.functional as F
import warp as wp
from lightning.pytorch.callbacks import (
    ModelCheckpoint,
    RichModelSummary,
    TQDMProgressBar,
)
from lightning.pytorch.core.module import LightningOptimizer, Optimizer
from lightning.pytorch.utilities.rank_zero import rank_zero_only
from omegaconf import DictConfig, OmegaConf
from torch import Tensor
from torch.utils.data import DataLoader
from torchmetrics.classification import MulticlassConfusionMatrix
from warpconvnet.dataset.scannet import ScanNetDataset
from warpconvnet.geometry.types.points import Points
from warpconvnet.models.internal.scripts.auto_resume_wandb_logger import (
    AutoResumeWandbLogger,
)
from warpconvnet.models.internal.scripts.hpc_utils import HPCSignalHandler, hpc_config
from warpconvnet.nn.modules.sparse_pool import PointToSparseWrapper


class ScanNetModule(pl.LightningModule):
    def __init__(self, model: torch.nn.Module, cfg: DictConfig):
        super().__init__()
        self.model = model
        self.cfg = cfg
        self.confusion_matrix = MulticlassConfusionMatrix(
            num_classes=cfg.data.num_classes, ignore_index=cfg.data.ignore_index
        )
        self.validation_step_outputs = []

        self.skip_current_optimizer_step_count = 0

    def forward(self, x):
        return self.model(x)

    def training_step(self, batch, batch_idx):
        data_time = time.time()
        st, batch_dict = self.prepare_batch(batch)
        data_time = time.time() - data_time

        start_time = time.time()
        output = self(st)
        loss = F.cross_entropy(
            output.features,
            batch_dict["labels"].long(),
            reduction="mean",
            ignore_index=self.cfg.data.ignore_index,
        )

        forward_time = time.time() - start_time
        lr = self.optimizers().param_groups[0]["lr"]

        # Log metrics in a single dictionary
        self.log_dict(
            {
                "train/lr": lr,
                "train/loss": loss,
                "train/time/forward": forward_time,
                "train/time/data": data_time,
            },
            on_step=True,
            on_epoch=False,
            prog_bar=True,
            sync_dist=True,
            batch_size=self.cfg.train.batch_size,
            rank_zero_only=True,
        )

        return loss

    def optimizer_step(
        self,
        epoch: int,
        batch_idx: int,
        optimizer: Union[Optimizer, LightningOptimizer],
        optimizer_closure: Optional[Callable[[], Any]] = None,
        **kwargs,
    ):
        """
        Skipping updates in case of unstable gradients
        https://github.com/Lightning-AI/lightning/issues/4956
        """
        time_start = time.time()
        valid_gradients = True
        rand_param_idx = random.randint(0, len(list(self.named_parameters())) - 1)
        for name, param in list(self.named_parameters())[rand_param_idx:]:
            if param.grad is not None:
                # valid_gradients = not (torch.isnan(param.grad).any() or torch.isinf(param.grad).any())
                valid_gradients = not (torch.isnan(param.grad).any())
                if not valid_gradients:
                    break
        if not valid_gradients:
            self.skip_current_optimizer_step_count += 1
            warnings.warn(
                f"detected inf or nan values in gradients. not updating model parameters. "
                f"Skipped {self.skip_current_optimizer_step_count} optimizer steps."
            )
            if self.skip_current_optimizer_step_count > 10:
                raise ValueError("Too many optimizer steps skipped. Check the loss function.")
            self.zero_grad()

        super().optimizer_step(epoch, batch_idx, optimizer, optimizer_closure, **kwargs)
        time_end = time.time()
        self.log(
            "train/time/backward",
            time_end - time_start,
            prog_bar=False,
            logger=True,
            on_step=True,
            on_epoch=False,
        )

    @torch.inference_mode()
    def validation_step(self, batch, batch_idx):
        st, batch_dict = self.prepare_batch(batch)

        output = self(st)
        loss = F.cross_entropy(
            output.features,
            batch_dict["labels"].long(),
            reduction="mean",
            ignore_index=self.cfg.data.ignore_index,
        )
        pred = output.features.argmax(dim=1)

        # Update confusion matrix locally on each GPU
        self.confusion_matrix.update(pred, batch_dict["labels"].long())

        self.validation_step_outputs.append(loss)

        return loss

    @rank_zero_only
    def print_summary(self, sample_input):
        if not self.summary_printed:
            self.summary_printed = True
            print(self.model)

    def on_validation_epoch_end(self):
        # Calculate average validation loss
        avg_loss = torch.stack(self.validation_step_outputs).mean()

        # Log validation loss
        self.log(
            "val/loss",
            avg_loss,
            on_step=False,
            on_epoch=True,
            prog_bar=True,
            sync_dist=True,
            rank_zero_only=True,
        )

        # Sync confusion matrix across all GPUs
        conf_matrix = self.confusion_matrix.compute()
        if dist.is_initialized():
            dist.all_reduce(conf_matrix)

        # Calculate and log metrics only on rank 0
        metrics = self.confusion_matrix_to_metrics(conf_matrix)
        self.log_dict(
            {"val/accuracy": metrics["accuracy"], "val/miou": metrics["miou"]},
            on_step=False,
            on_epoch=True,
            prog_bar=True,
            sync_dist=False,
            rank_zero_only=True,
        )

        # Reset for next epoch
        self.confusion_matrix.reset()
        self.validation_step_outputs.clear()

    def configure_optimizers(self):
        # Create optimizer using Hydra instantiate
        optimizer = hydra.utils.instantiate(self.cfg.optimizer, params=self.parameters())

        # Extract Lightning-specific parameters before instantiating scheduler
        scheduler_cfg = OmegaConf.to_container(self.cfg.scheduler, resolve=True)
        lightning_scheduler_dict = {
            "interval": scheduler_cfg.pop("interval", "epoch"),
            "frequency": scheduler_cfg.pop("frequency", 1),
        }

        assert lightning_scheduler_dict.get("interval") in [
            "step",
            "epoch",
        ], f"Invalid scheduler interval: {lightning_scheduler_dict.get('interval')}"

        # Create scheduler using Hydra instantiate (without Lightning-specific params)
        scheduler = hydra.utils.instantiate(scheduler_cfg, optimizer=optimizer)
        lightning_scheduler_dict["scheduler"] = scheduler

        return {
            "optimizer": optimizer,
            "lr_scheduler": lightning_scheduler_dict,
        }

    def prepare_batch(self, batch: Dict[str, List[Tensor]]) -> Tuple[Points, Dict[str, Tensor]]:
        cat_batch_dict = {k: torch.cat(v, dim=0) for k, v in batch.items()}
        st = Points.from_list_of_coordinates(
            batch["coords"],
            features=batch["colors"],
        ).to(self.device)
        return st, cat_batch_dict

    @staticmethod
    def confusion_matrix_to_metrics(conf_matrix: torch.Tensor) -> Dict[str, float]:
        conf_matrix = conf_matrix.cpu()
        accuracy = (conf_matrix.diag().sum() / conf_matrix.sum()).item() * 100
        class_iou = conf_matrix.diag() / (
            conf_matrix.sum(dim=1) + conf_matrix.sum(dim=0) - conf_matrix.diag()
        )
        miou = class_iou.mean().item() * 100
        return {"accuracy": accuracy, "miou": miou}


def collate_fn(batch: List[Dict[str, Tensor]]):
    return {key: [torch.tensor(item[key]) for item in batch] for key in batch[0].keys()}


@hydra.main(config_path="../configs", config_name="scannet.yaml")
def main(cfg: DictConfig) -> None:
    cfg = hpc_config(cfg)
    pl.seed_everything(cfg.seed)

    # Data
    train_dataset = ScanNetDataset(cfg.paths.data_dir, split="train")
    val_dataset = ScanNetDataset(cfg.paths.data_dir, split="val")

    train_loader = DataLoader(
        train_dataset,
        batch_size=cfg.train.batch_size,
        num_workers=cfg.train.num_workers,
        shuffle=True,
        collate_fn=collate_fn,
        persistent_workers=True,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=cfg.test.batch_size,
        num_workers=cfg.test.num_workers,
        shuffle=False,
        collate_fn=collate_fn,
        persistent_workers=True,
    )

    # Model
    model = hydra.utils.instantiate(cfg.model)
    if hasattr(cfg.model, "in_type") and cfg.model.in_type == "voxel":
        model = PointToSparseWrapper(
            inner_module=model,
            voxel_size=cfg.data.voxel_size,
            concat_unpooled_pc=False,
        )

    # Lightning module
    lightning_module = ScanNetModule(model, cfg)

    # Callbacks
    checkpoint_callback = ModelCheckpoint(
        dirpath=os.path.join(cfg.paths.output_dir, "checkpoints"),
        filename="latest",
        save_last=True,
        save_top_k=1,
        every_n_epochs=1,
    )

    class CustomTQDMProgressBar(TQDMProgressBar):
        def get_metrics(self, trainer, model):
            items = super().get_metrics(trainer, model)
            items.pop("v_num", None)
            return items

    progress_bar = CustomTQDMProgressBar(refresh_rate=cfg.train.get("log_every_n_steps", 10))

    # Add RichModelSummary callback
    rich_model_summary = RichModelSummary(max_depth=3)

    # Logger
    if cfg.use_wandb:
        logger = AutoResumeWandbLogger(
            project="scannet-segmentation",
            name=cfg.get("wandb_name", None),
            save_dir=cfg.paths.output_dir,
            id=os.environ.get("SLURM_JOB_ID"),
            config=OmegaConf.to_container(cfg, resolve=True),
        )
    else:
        logger = True

    # Determine the appropriate strategy based on the number of available GPUs
    num_gpus = torch.cuda.device_count()
    strategy = "auto"
    if num_gpus > 1:
        from lightning.pytorch.strategies import DDPStrategy

        strategy = DDPStrategy()

    # Trainer
    trainer = pl.Trainer(
        max_epochs=cfg.train.epochs,
        accelerator="gpu",
        devices="auto",
        strategy=strategy,
        logger=logger,
        callbacks=[
            checkpoint_callback,
            progress_bar,
            rich_model_summary,
        ],  # Add rich_model_summary here
        default_root_dir=cfg.paths.output_dir,
        gradient_clip_val=cfg.train.get("gradient_clip_val", None),
        log_every_n_steps=cfg.train.get("log_every_n_steps", 1),
        precision=cfg.get("precision", "32-true"),
    )

    # Check for the latest checkpoint
    checkpoint_dir = os.path.join(cfg.paths.output_dir, "checkpoints")
    latest_checkpoint = None
    if os.path.exists(checkpoint_dir):
        checkpoints = [f for f in os.listdir(checkpoint_dir) if f.endswith(".ckpt")]
        if checkpoints:
            latest_checkpoint = os.path.join(
                checkpoint_dir,
                max(
                    checkpoints,
                    key=lambda x: os.path.getctime(os.path.join(checkpoint_dir, x)),
                ),
            )

    # HPC Signal Handler
    with HPCSignalHandler(trainer):
        # Train and validate
        ckpt_path = latest_checkpoint if latest_checkpoint else None
        print(
            f"{'Resuming from checkpoint:' if ckpt_path else 'Starting training from scratch'} {ckpt_path or ''}"
        )
        trainer.fit(
            lightning_module,
            train_loader,
            val_loader,
            ckpt_path=ckpt_path,
        )


if __name__ == "__main__":
    wp.init()
    num_gpus = torch.cuda.device_count()
    if num_gpus > 1:
        dist.init_process_group(backend="nccl")
    main()
    if num_gpus > 1:
        dist.destroy_process_group()
