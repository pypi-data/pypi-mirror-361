# Use hydra config to run this file
#
# Points inputs
# python examples/modelnet.py train.batch_size=32 model=pointnet model.in_channels=24 data.out_type=point
# python examples/modelnet.py train.batch_size=32 model=dgcnn model.in_channels=24 data.out_type=point
#
# Voxels inputs
# python examples/modelnet.py train.batch_size=32 model=sparse_convnet model.in_channels=24 data.out_type=voxel
from typing import Dict, Literal, Optional, Tuple

try:
    import hydra
    from omegaconf import DictConfig, OmegaConf
except ImportError:
    print("Hydra not installed, pip install hydra-core --upgrade")
    exit(1)

from tqdm import tqdm

try:
    import wandb
except ImportError:
    wandb = None

import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import warp as wp
from torch import Tensor
from torch.utils.data import DataLoader
from torchmetrics.classification import MulticlassConfusionMatrix
from warpconvnet.dataset.modelnet import ModelNet40Dataset
from warpconvnet.geometry.types.points import Points
from warpconvnet.geometry.types.voxels import Voxels
from warpconvnet.nn.modules.base_module import BaseSpatialModel


class DataToTensor:
    def __init__(
        self,
        voxel_size: float = 0.02,
        encoding_channels: int = 8,
        encoding_range: float = 1,
        out_type: Literal["point", "voxel"] = "voxel",
        device: str = "cuda",
    ):
        assert out_type in ["point", "voxel"]
        self.voxel_size = voxel_size
        self.encoding_channels = encoding_channels
        self.encoding_range = encoding_range
        self.device = device
        self.out_type = out_type

    def __call__(self, batch: Dict[str, Tensor]) -> Voxels:
        """
        Collate function for ModelNet40Dataset
        """
        pc = Points.from_list_of_coordinates(
            batch["coords"],
            encoding_channels=self.encoding_channels,
            encoding_range=self.encoding_range,
        ).to(self.device)
        if self.out_type == "point":
            return pc
        else:
            st: Voxels = pc.to_sparse(voxel_size=self.voxel_size)
            return st


def confusion_matrix_to_metrics(conf_matrix: Tensor) -> Dict[str, float]:
    """
    Return accuracy, miou, class_iou, class_accuracy

    Rows are ground truth, columns are predictions.
    """
    conf_matrix = conf_matrix.cpu()
    accuracy = (conf_matrix.diag().sum() / conf_matrix.sum()).item() * 100
    class_accuracy = (conf_matrix.diag() / conf_matrix.sum(dim=1)) * 100
    class_iou = conf_matrix.diag() / (
        conf_matrix.sum(dim=1) + conf_matrix.sum(dim=0) - conf_matrix.diag()
    )
    miou = class_iou.mean().item() * 100
    return {
        "accuracy": accuracy,
        "miou": miou,
        "class_iou": class_iou,
        "class_accuracy": class_accuracy,
    }


def train(
    model: nn.Module,
    train_loader: DataLoader,
    optimizer: optim.Optimizer,
    epoch: int,
    cfg: DictConfig,
):
    model.train()
    bar = tqdm(train_loader)
    data_prep = DataToTensor(
        cfg.data.voxel_size,
        cfg.data.encoding_channels,
        cfg.data.encoding_range,
        cfg.data.out_type,
        cfg.device,
    )
    for batch_idx, batch_dict in enumerate(bar):
        optimizer.zero_grad()
        torch.cuda.empty_cache()
        st = data_prep(batch_dict)
        output = model(st)
        loss = F.cross_entropy(
            output,
            batch_dict["labels"].long().to(output.device),
            reduction="mean",
            ignore_index=cfg.data.ignore_index,
        )
        loss.backward()
        optimizer.step()
        bar.set_description(f"Train Epoch: {epoch} Loss: {loss.item():.3f}")
        if cfg.use_wandb:
            wandb.log(
                {
                    "train/loss": loss.item(),
                    "train/lr": optimizer.param_groups[0]["lr"],
                    "epoch": epoch,
                }
            )


@torch.inference_mode()
def test(
    model: nn.Module,
    test_loader: DataLoader,
    cfg: DictConfig,
    num_test_batches: Optional[int] = None,
):
    model.eval()
    torch.cuda.empty_cache()
    confusion_matrix = MulticlassConfusionMatrix(
        num_classes=cfg.data.num_classes, ignore_index=cfg.data.ignore_index
    ).to(cfg.device)
    data_prep = DataToTensor(
        cfg.data.voxel_size,
        cfg.data.encoding_channels,
        cfg.data.encoding_range,
        cfg.data.out_type,
        cfg.device,
    )
    for batch_idx, batch_dict in enumerate(test_loader):
        st = data_prep(batch_dict)
        output = model(st)
        pred = output.argmax(dim=1)
        labels = batch_dict["labels"].long().to(pred.device)
        confusion_matrix.update(pred, labels)
        if num_test_batches is not None and batch_idx >= num_test_batches:
            break

    metrics = confusion_matrix_to_metrics(confusion_matrix.compute())
    if cfg.use_wandb:
        wandb.log(metrics)
    return metrics


@hydra.main(config_path="../configs", config_name="modelnet.yaml")
def main(cfg):
    wp.init()
    # instantiate model
    model = hydra.utils.instantiate(cfg.model).to(cfg.device)

    train_dataloader = DataLoader(
        ModelNet40Dataset(root_dir=cfg.data.root_dir, split="train"),
        batch_size=cfg.train.batch_size,
        shuffle=True,
        num_workers=cfg.train.num_workers,
    )
    test_dataloader = DataLoader(
        ModelNet40Dataset(root_dir=cfg.data.root_dir, split="test"),
        batch_size=cfg.test.batch_size,
        shuffle=False,
        num_workers=cfg.test.num_workers,
    )

    optimizer = optim.AdamW(model.parameters(), lr=cfg.train.lr)
    scheduler = optim.lr_scheduler.StepLR(
        optimizer, step_size=cfg.train.step_size, gamma=cfg.train.gamma
    )

    if cfg.use_wandb:
        wandb.init(
            project="modelnet40-classification",
            config=OmegaConf.to_container(cfg),
        )

    # test before training
    metrics = test(model, test_dataloader, cfg, num_test_batches=10)
    print(f"Initial accuracy: {metrics['accuracy']:.2f}%, mIoU: {metrics['miou']:.2f}%")
    for epoch in range(1, cfg.train.epochs + 1):
        train(model, train_dataloader, optimizer, epoch, cfg)
        metrics = test(model, test_dataloader, cfg)
        print(f"Epoch {epoch} accuracy: {metrics['accuracy']:.2f}%, mIoU: {metrics['miou']:.2f}%")
        scheduler.step()

    print(f"Final metrics: {metrics}")


if __name__ == "__main__":
    main()
