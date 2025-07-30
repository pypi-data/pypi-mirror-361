from abc import ABC, abstractmethod
from typing import List, Optional, Type

import torch
import torch.nn as nn
from torch.nn import functional as F
from warpconvnet.geometry.types.voxels import Voxels
from warpconvnet.nn.functional.transforms import cat as sparse_cat
from warpconvnet.nn.modules.activations import ReLU as SparseReLU
from warpconvnet.nn.modules.normalizations import BatchNorm as SparseBatchNorm
from warpconvnet.nn.modules.sparse_conv import SparseConv3d


def pad_to_match(x, y):
    """
    Pad x to match the spatial sparsity of y
    """
    spatial_shape = x.shape[2:]
    y_spatial_shape = y.shape[2:]
    padding = [max(0, y_spatial_shape[i] - spatial_shape[i]) for i in range(len(spatial_shape))]
    if any(padding):
        new_x = torch.zeros(
            x.shape[0],
            x.shape[1],
            y_spatial_shape[0],
            y_spatial_shape[1],
            y_spatial_shape[2],
            device=x.device,
        )
        new_x[:, :, : spatial_shape[0], : spatial_shape[1], : spatial_shape[2]] = x
        return new_x
    return x


def tensor_concat(x, y, dim=1):
    """
    Concatenate two tensors, converting y to x type if necessary.
    """
    if isinstance(x, Voxels) and not isinstance(y, Voxels):
        y = Voxels.from_dense(y, target_spatial_sparse_tensor=x)
    elif not isinstance(x, Voxels) and isinstance(y, Voxels):
        y = y.to_dense()

    if isinstance(x, Voxels):
        return sparse_cat(x, y)
    else:
        x = pad_to_match(x, y)
        return torch.cat((x, y), dim=dim)


class ConvBlockBase(nn.Module, ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def forward(self, x, out_spatial_sparsity=None):
        pass

    def convert_input(self, x):
        # Default implementation: do nothing
        return x

    def convert_output(self, x):
        # Default implementation: do nothing
        return x


class BasicBlockBase(nn.Module, ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def forward(self, x):
        pass


class SparseConvBlock(ConvBlockBase):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int = 3,
        stride: int = 1,
        bias: bool = False,
        transposed: bool = False,
        activation: Optional[nn.Module] = None,
    ):
        super().__init__()
        if activation is None:
            activation = SparseReLU(inplace=True)

        self.conv = SparseConv3d(
            in_channels,
            out_channels,
            kernel_size,
            stride,
            bias=bias,
            transposed=transposed,
        )
        self.bn = SparseBatchNorm(out_channels)
        self.act = activation

    def forward(
        self,
        x: Voxels,
        from_dense_spatial_sparsity=None,
        transposed_out_spatial_sparsity=None,
    ):
        x = self.convert_input(x, from_dense_spatial_sparsity)

        if self.conv.transposed:
            assert (
                transposed_out_spatial_sparsity is not None
            ), "Output spatial sparsity is required for transposed convolution"
            x = self.conv(x, transposed_out_spatial_sparsity)
        else:
            x = self.conv(x)
        x = self.bn(x)
        x = self.act(x)
        return x

    def convert_input(self, x, from_dense_spatial_sparsity):
        if isinstance(x, torch.Tensor):
            assert (
                from_dense_spatial_sparsity is not None
            ), "Input spatial sparsity is required for dense tensor"
            assert isinstance(
                from_dense_spatial_sparsity, Voxels
            ), "Input spatial sparsity must be a Voxels"
            # Convert dense tensor to sparse tensor
            # Assuming we have a method to create a sparse tensor from dense
            x = Voxels.from_dense(
                x, target_spatial_sparse_tensor=from_dense_spatial_sparsity
            )
        return x


class DenseConvBlock(ConvBlockBase):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int = 3,
        stride: int = 1,
        bias: bool = False,
        transposed: bool = False,
        activation: Optional[nn.Module] = None,
    ):
        super().__init__()
        if activation is None:
            activation = nn.ReLU(inplace=True)

        self.transposed = transposed
        padding = kernel_size // 2  # Maintain spatial dimensions
        if transposed:
            self.conv = nn.ConvTranspose3d(
                in_channels,
                out_channels,
                kernel_size,
                stride,
                padding=padding,
                bias=bias,
            )
        else:
            self.conv = nn.Conv3d(
                in_channels,
                out_channels,
                kernel_size,
                stride,
                padding=padding,
                bias=bias,
            )
        self.bn = nn.BatchNorm3d(out_channels)
        self.act = activation

    def forward(
        self,
        x: torch.Tensor,
        from_dense_spatial_sparsity=None,
        transposed_out_spatial_sparsity=None,
    ):
        x = self.convert_input(x)

        x = self.conv(x)
        x = self.bn(x)
        x = self.act(x)
        return x

    def convert_input(self, x):
        if isinstance(x, Voxels):
            x = x.to_dense()
        return x

    def pad_transposed_output(self, x, transposed_out_spatial_sparsity):

        return x


class SparseBasicBlock(BasicBlockBase):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        bias: bool = False,
    ):
        super().__init__()
        self.conv1 = SparseConvBlock(
            in_channels,
            out_channels,
            kernel_size=3,
            stride=1,
            bias=bias,
            activation=SparseReLU(inplace=True),
        )
        self.conv2 = SparseConvBlock(
            out_channels,
            out_channels,
            kernel_size=3,
            bias=bias,
            activation=None,
        )
        self.downsample = None
        if in_channels != out_channels:
            self.downsample = SparseConvBlock(
                in_channels,
                out_channels,
                kernel_size=1,
                stride=1,
                bias=bias,
                activation=None,
            )
        self.relu = SparseReLU(inplace=True)

    def forward(self, x: Voxels, out_spatial_sparsity=None):
        x = self.convert_input(x, out_spatial_sparsity)
        identity = x

        out = self.conv1(x)
        out = self.conv2(out)
        if self.downsample is not None:
            identity = self.downsample(x)
        out = out + identity
        out = self.relu(out)
        return out

    def convert_input(self, x, out_spatial_sparsity):
        if isinstance(x, torch.Tensor):
            x = Voxels.from_dense(
                x, target_spatial_sparse_tensor=out_spatial_sparsity
            )
        return x


class DenseBasicBlock(BasicBlockBase):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        bias: bool = False,
    ):
        super().__init__()
        self.conv1 = DenseConvBlock(
            in_channels,
            out_channels,
            kernel_size=3,
            stride=1,
            bias=bias,
            activation=nn.ReLU(inplace=True),
        )
        self.conv2 = DenseConvBlock(
            out_channels,
            out_channels,
            kernel_size=3,
            bias=bias,
            activation=None,
        )
        self.downsample = None
        if in_channels != out_channels:
            self.downsample = DenseConvBlock(
                in_channels,
                out_channels,
                kernel_size=1,
                stride=1,
                bias=bias,
                activation=None,
            )
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x: torch.Tensor, out_spatial_sparsity=None):
        x = self.convert_input(x)
        identity = x
        out = self.conv1(x)
        out = self.conv2(out)
        if self.downsample is not None:
            identity = self.downsample(x)
        out = out + identity
        out = self.relu(out)
        return out

    def convert_input(self, x):
        if isinstance(x, Voxels):
            x = x.to_dense()
        return x


def get_conv_block(block_type: str):
    if block_type == "sparse":
        return SparseConvBlock
    elif block_type == "dense":
        return DenseConvBlock
    else:
        raise ValueError(f"Unknown block type: {block_type}")


def get_basic_block(block_type: str):
    if block_type == "sparse":
        return SparseBasicBlock
    elif block_type == "dense":
        return DenseBasicBlock
    else:
        raise ValueError(f"Unknown block type: {block_type}")
