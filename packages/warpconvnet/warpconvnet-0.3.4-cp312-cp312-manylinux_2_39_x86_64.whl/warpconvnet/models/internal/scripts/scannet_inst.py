# Use hydra config to run the script
# python examples/scannet.py train.batch_size=12 model=sparse_convunet model.in_channels=3
# python examples/scannet.py train.batch_size=12 model=mink_unet
# python examples/scannet.py train.batch_size=4 model=point_transformer model.out_type=segmentation model.out_channels=20 use_wandb=false train.batch_size=2 test.batch_size=2
import os
from typing import Dict, List

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
from lightning.pytorch.utilities.rank_zero import rank_zero_only
from omegaconf import DictConfig, OmegaConf
from torch import Tensor
from torch.utils.data import DataLoader
from warpconvnet.geometry.types.voxels import Voxels
from warpconvnet.models.internal.scripts.auto_resume_wandb_logger import (
    AutoResumeWandbLogger,
)
from warpconvnet.models.internal.scripts.datasets.scannet_inst_dataset import (
    ScanNet200Dataset,
)
from warpconvnet.models.internal.scripts.hpc_utils import HPCSignalHandler, hpc_config
from warpconvnet.models.internal.scripts.mask_loss import SetCriterion
from warpconvnet.utils.nested import to_nested


class ScanNetModule(pl.LightningModule):
    def __init__(self, model: torch.nn.Module, cfg: DictConfig):
        super().__init__()
        self.model = model
        self.cfg = cfg
        self.validation_step_outputs = []
        self.criterion = SetCriterion(losses=["mask"])

    def forward(self, x):
        return self.model(x)

    def training_step(self, batch_dict, batch_idx):
        torch.cuda.empty_cache()
        st = self.to_sparse_tensor(batch_dict)

        scene_features, masks = self(st)
        loss_dict, match_cost = self.criterion(
            masks,
            to_nested(batch_dict["instance"], batch_dict["offsets"]),
        )
        loss = 0
        for k, v in loss_dict.items():
            loss += v

        # Log metrics in a single dictionary
        self.log_dict(
            {
                "train/lr": self.optimizers().param_groups[0]["lr"],
                "train/loss": loss,
                "train/match_cost": match_cost,
                **{f"train/{k}": v for k, v in loss_dict.items()},
            },
            on_step=True,
            on_epoch=False,
            prog_bar=True,
            sync_dist=True,
            batch_size=self.cfg.train.batch_size,
        )

        return loss

    @torch.inference_mode()
    def validation_step(self, batch_dict, batch_idx):
        st = self.to_sparse_tensor(batch_dict)
        scene_features, masks = self(st)
        loss_dict, match_cost = self.criterion(
            masks,
            to_nested(batch_dict["instance"], batch_dict["offsets"]),
        )
        # IoU evaluation?
        self.validation_step_outputs.append(loss_dict)
        return loss_dict

    @rank_zero_only
    def print_summary(self, sample_input):
        if not self.summary_printed:
            self.summary_printed = True
            print(self.model)

    def on_validation_epoch_end(self):
        # Calculate average validation loss
        out_dict = {}
        for k, v in self.validation_step_outputs[0].items():
            out_dict[f"val/{k}"] = torch.stack(
                [d[k] for d in self.validation_step_outputs]
            ).mean()

        # Log validation loss
        self.log_dict(
            out_dict,
            on_step=False,
            on_epoch=True,
            prog_bar=True,
            sync_dist=True,
            rank_zero_only=True,
        )

        self.validation_step_outputs.clear()

    def configure_optimizers(self):
        optimizer = torch.optim.AdamW(self.parameters(), lr=self.cfg.train.lr)
        scheduler = torch.optim.lr_scheduler.StepLR(
            optimizer, step_size=self.cfg.train.step_size, gamma=self.cfg.train.gamma
        )
        return {"optimizer": optimizer, "lr_scheduler": scheduler}

    def to_sparse_tensor(self, batch: Dict[str, List[Tensor]]) -> Voxels:
        st = Voxels(
            batched_coordinates=batch["coord_int"],
            batched_features=batch["color"],
            offsets=batch["offsets"],
        ).to(self.device)
        return st


def collate_fn(batch: List[Dict]):
    Ns = [0] + [len(item["coord"]) for item in batch]
    offsets = torch.cumsum(torch.tensor(Ns), dim=0)
    cat_dict = {
        k: (
            torch.cat([torch.tensor(item[k]) for item in batch])
            if isinstance(batch[0][k], np.ndarray)
            else [item[k] for item in batch]
        )
        for k in batch[0].keys()
    }
    cat_dict["offsets"] = offsets
    return cat_dict


@hydra.main(config_path="../../configs", config_name="scannet_inst.yaml")
def main(cfg: DictConfig) -> None:
    cfg = hpc_config(cfg)
    pl.seed_everything(cfg.seed)

    # Data
    train_dataset = ScanNet200Dataset(
        data_root=cfg.paths.data_dir, split="train", voxel_size=cfg.data.voxel_size
    )
    val_dataset = ScanNet200Dataset(
        data_root=cfg.paths.data_dir, split="val", voxel_size=cfg.data.voxel_size
    )

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

    progress_bar = CustomTQDMProgressBar(
        refresh_rate=cfg.train.get("log_every_n_steps", 10)
    )

    # Add RichModelSummary callback
    rich_model_summary = RichModelSummary(max_depth=3)

    # Logger
    if cfg.use_wandb:
        logger = AutoResumeWandbLogger(
            project="scannet-instance",
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


class DistWrapper:
    def __init__(self, num_gpus: int):
        self.num_gpus = num_gpus

    def __enter__(self):
        if self.num_gpus > 1:
            dist.init_process_group(backend="nccl")

    def __exit__(self, exc_type, exc_value, traceback):
        if self.num_gpus > 1:
            dist.destroy_process_group()


if __name__ == "__main__":
    wp.init()
    with DistWrapper(torch.cuda.device_count()):
        main()
