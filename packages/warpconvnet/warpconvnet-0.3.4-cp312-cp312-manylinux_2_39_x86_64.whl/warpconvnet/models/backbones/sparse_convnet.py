from typing import Optional

import torch
from jaxtyping import Float
from torch import Tensor, nn
from warpconvnet.geometry.types.points import Points
from warpconvnet.geometry.types.voxels import Voxels
from warpconvnet.nn.modules.activations import ReLU
from warpconvnet.nn.modules.normalizations import BatchNorm
from warpconvnet.nn.modules.sparse_conv import SparseConv3d


class SparseConvNet(nn.Module):
    """
    Example network that showcases the use of point conv, sparse conv, and dense conv in one model.
    """

    def __init__(
        self,
        in_channels: int = 3,
        out_channels: int = 40,
        sparse_kernel_size: int = 3,
    ):
        super().__init__()
        self.out_channels = out_channels
        self.sparse_conv = nn.Sequential(
            SparseConv3d(in_channels, 64, kernel_size=sparse_kernel_size, stride=1),
            BatchNorm(64),
            ReLU(),
            SparseConv3d(64, 64, kernel_size=sparse_kernel_size, stride=2),  # stride
            BatchNorm(64),
            ReLU(),
            SparseConv3d(64, 128, kernel_size=sparse_kernel_size, stride=1),
            BatchNorm(128),
            ReLU(),
            SparseConv3d(128, 256, kernel_size=sparse_kernel_size, stride=2),  # stride
            BatchNorm(256),
            ReLU(),
            SparseConv3d(256, 512, kernel_size=sparse_kernel_size, stride=1),
            BatchNorm(512),
            ReLU(),
        )
        self.dense_conv = nn.Sequential(
            nn.Conv3d(512, 1024, kernel_size=2, stride=2),
            nn.BatchNorm3d(1024),
            nn.ReLU(),
            nn.Conv3d(1024, 1024, kernel_size=2, stride=2),
            nn.BatchNorm3d(1024),
            nn.ReLU(),
            nn.Flatten(),
            nn.Dropout(0.5),
            nn.Linear(1024 * 2 * 2 * 2, 1024),
            nn.BatchNorm1d(1024),
            nn.ReLU(),
            nn.Linear(1024, out_channels),
        )

    def forward(self, st: Voxels) -> Float[Tensor, "B out_channels"]:
        st = self.sparse_conv(st)
        dt: Tensor = st.to_dense(channel_dim=1, min_coords=(-5, -5, -5), max_coords=(4, 4, 4))
        pred = self.dense_conv(dt)
        return pred
