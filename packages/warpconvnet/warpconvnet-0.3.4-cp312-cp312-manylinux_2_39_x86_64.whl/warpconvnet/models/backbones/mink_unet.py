import functools
from typing import Callable, List, Literal, Optional, Union

import torch
import torch.nn as nn
from jaxtyping import Float
from torch import Tensor
from warpconvnet.geometry.coords.search.search_configs import (
    RealSearchConfig,
    RealSearchMode,
)
from warpconvnet.geometry.types.points import Points
from warpconvnet.geometry.types.voxels import Voxels
from warpconvnet.nn.functional.point_pool import point_pool
from warpconvnet.nn.functional.point_unpool import point_unpool
from warpconvnet.nn.functional.transforms import cat
from warpconvnet.nn.modules.activations import ReLU
from warpconvnet.nn.modules.attention import (
    PatchAttention,
    SpatialFeatureAttention,
    TransformerBlock,
)
from warpconvnet.nn.modules.point_conv import PointConv
from warpconvnet.nn.modules.sequential import Sequential
from warpconvnet.nn.modules.sparse_conv import SparseConv3d


class ConvBlock(Sequential):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int = 3,
        stride: int = 1,
        activation: Optional[nn.Module] = nn.ReLU(inplace=True),
        bias: bool = False,
        compute_dtype: Optional[torch.dtype] = None,
    ):
        super().__init__(
            SparseConv3d(
                in_channels,
                out_channels,
                kernel_size,
                stride,
                bias=bias,
                compute_dtype=compute_dtype,
            ),
            nn.BatchNorm1d(out_channels),
            nn.Identity() if activation is None else activation,
        )


class ConvTrBlock(nn.Module):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        kernel_size: int = 3,
        stride: int = 1,
        activation: Optional[nn.Module] = nn.ReLU(inplace=True),
        bias: bool = False,
        compute_dtype: Optional[torch.dtype] = None,
    ):
        super().__init__()
        self.conv_tr = SparseConv3d(
            in_channels,
            out_channels,
            kernel_size,
            stride,
            transposed=True,
            bias=bias,
            compute_dtype=compute_dtype,
        )
        self.norm_act = Sequential(
            nn.BatchNorm1d(out_channels), nn.Identity() if activation is None else activation
        )

    def forward(
        self,
        x: Voxels,
        out_spatial_sparsity: Voxels,
    ) -> Voxels:
        out = self.conv_tr(x, out_spatial_sparsity)
        out = self.norm_act(out)
        return out


class BasicBlock(nn.Module):
    expansion = 1

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        stride: int = 1,
        bias: bool = False,
        compute_dtype: Optional[torch.dtype] = None,
    ):
        super().__init__()
        self.conv1 = ConvBlock(
            in_channels,
            out_channels,
            kernel_size=3,
            stride=stride,
            bias=bias,
            compute_dtype=compute_dtype,
        )
        self.conv2 = ConvBlock(
            out_channels,
            out_channels,
            kernel_size=3,
            activation=None,
            bias=bias,
            compute_dtype=compute_dtype,
        )

        self.downsample = None
        if stride != 1 or in_channels != out_channels:
            self.downsample = ConvBlock(
                in_channels,
                out_channels,
                kernel_size=1,
                stride=stride,
                activation=None,
                bias=bias,
                compute_dtype=compute_dtype,
            )

        self.relu = ReLU(inplace=True)

    def forward(self, x: Float[Tensor, "N C"]) -> Float[Tensor, "N C"]:
        identity = x

        out = self.conv1(x)
        out = self.conv2(out)

        if self.downsample is not None:
            identity = self.downsample(x)

        out += identity
        out = self.relu(out)

        return out


class BottleneckBlock(nn.Module):
    expansion = 4

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        stride: int = 1,
        bias: bool = False,
        compute_dtype: Optional[torch.dtype] = None,
    ):
        super().__init__()
        mid_channels = out_channels // self.expansion

        self.conv1 = ConvBlock(
            in_channels,
            mid_channels,
            kernel_size=1,
            bias=bias,
            compute_dtype=compute_dtype,
        )
        self.conv2 = ConvBlock(
            mid_channels,
            mid_channels,
            kernel_size=3,
            stride=stride,
            bias=bias,
            compute_dtype=compute_dtype,
        )
        self.conv3 = ConvBlock(
            mid_channels,
            out_channels,
            kernel_size=1,
            activation=None,
            bias=bias,
            compute_dtype=compute_dtype,
        )

        self.downsample = None
        if stride != 1 or in_channels != out_channels:
            self.downsample = ConvBlock(
                in_channels,
                out_channels,
                kernel_size=1,
                stride=stride,
                activation=None,
                bias=bias,
                compute_dtype=compute_dtype,
            )

        self.relu = ReLU(inplace=True)

    def forward(self, x: Float[Tensor, "N C"]) -> Float[Tensor, "N C"]:
        identity = x

        out = self.conv1(x)
        out = self.conv2(out)
        out = self.conv3(out)

        if self.downsample is not None:
            identity = self.downsample(x)

        out += identity
        out = self.relu(out)

        return out


class ConvTransformerBlock(nn.Module):
    """
    Basic block followed by an attention block.
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        num_heads: int,
        BLOCK: nn.Module = BasicBlock,
        qkv_bias: bool = False,
        qk_scale: Optional[float] = None,
        attn_drop: float = 0.0,
        proj_drop: float = 0.0,
        ffn_multiplier: int = 2,
        norm_eps: float = 1e-5,
        norm_fn: Optional[Callable[[int], nn.Module]] = None,
        attn_fn: Optional[Callable[[Voxels], Voxels]] = None,
        compute_dtype: Optional[torch.dtype] = None,
    ):
        super().__init__()
        self.residual = BLOCK(
            in_channels,
            out_channels,
            stride=1,
            compute_dtype=compute_dtype,
        )
        self.transformer = TransformerBlock(
            dim=out_channels,
            num_heads=num_heads,
            qkv_bias=qkv_bias,
            qk_scale=qk_scale,
            attn_drop=attn_drop,
            proj_drop=proj_drop,
            ffn_multiplier=ffn_multiplier,
            norm_eps=norm_eps,
            attn_fn=attn_fn,
        )

    def forward(self, x: Voxels) -> Voxels:
        x = self.residual(x)
        x = self.transformer(x)
        return x


class MinkUNetBase(nn.Module):
    """
    MinkUNetBase is a base class for MinkUNet models.
    It is based on the implementation from MinkowskiEngine, with minor modifications for readability.

    Source: https://github.com/NVIDIA/MinkowskiEngine/blob/master/examples/minkunet.py
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        planes: tuple[int, ...],
        layers: tuple[int, ...],
        init_dim: int = 32,
        block_types: Union[str, List[Literal["block", "attn", "pattn"]]] = "bbbbbbbb",
        num_heads: Optional[Union[int, List[int]]] = None,
        patch_sizes: Union[int, List[int]] = 1024,
        BLOCK: Union[str, nn.Module] = BasicBlock,
        compute_dtype: Optional[torch.dtype] = torch.float32,
        **kwargs,
    ):
        super().__init__()

        if isinstance(block_types, str) and len(block_types) == 8:
            list_block_types = []
            for i, block_type in enumerate(block_types.lower()):
                assert block_type in ["b", "a", "p"]
                if block_type == "b":
                    list_block_types.append("block")
                elif block_type == "a":
                    list_block_types.append("attn")
                elif block_type == "p":
                    list_block_types.append("pattn")
            block_types = list_block_types
        if isinstance(block_types, str) and block_types in ["block", "attn", "pattn"]:
            block_types = [block_types] * len(planes)
        if isinstance(patch_sizes, int):
            patch_sizes = [patch_sizes] * len(planes)
        if isinstance(num_heads, int):
            num_heads = [num_heads] * len(planes)

        assert len(block_types) == len(planes)
        assert len(planes) == len(layers)

        if isinstance(BLOCK, str):
            assert BLOCK in ["basic", "bottleneck"], f"Unknown block type: {BLOCK}"
            BLOCK = BasicBlock if BLOCK == "basic" else BottleneckBlock

        # Create lists of block modules and their kwargs
        blocks = []
        block_kwargs = []
        for i, block_type in enumerate(block_types):
            assert block_type in [
                "block",
                "attn",
                "pattn",
            ], f"Unknown block type: {block_type} in block_types: {block_types}"
            if block_type == "block":
                blocks.append(BLOCK)
                block_kwargs.append({})
            elif block_type == "attn":
                assert num_heads is not None, "num_heads must be provided for attn blocks"
                assert len(num_heads) == len(planes)
                blocks.append(ConvTransformerBlock)
                block_kwargs.append(
                    {
                        "BLOCK": BLOCK,
                        "num_heads": num_heads[i],
                        "attn_fn": functools.partial(
                            SpatialFeatureAttention,
                            use_encoding=False,
                        ),
                    }
                )
            elif block_type == "pattn":
                assert num_heads is not None, "num_heads must be provided for pattn blocks"
                assert len(num_heads) == len(planes)
                assert len(patch_sizes) == len(planes)
                blocks.append(ConvTransformerBlock)
                block_kwargs.append(
                    {
                        "BLOCK": BLOCK,
                        "num_heads": num_heads[i],
                        "attn_fn": functools.partial(
                            PatchAttention,
                            patch_size=patch_sizes[i],
                            rand_perm_patch=True,
                        ),
                    }
                )
            else:
                raise ValueError(f"Unknown block type: {block_type}")

        self.PLANES = planes
        self.LAYERS = layers
        self.INIT_DIM = init_dim

        # Initial convolution
        self.conv0 = ConvBlock(
            in_channels, init_dim, kernel_size=5, bias=True, compute_dtype=compute_dtype
        )

        # Downsampling path
        self.conv1 = ConvBlock(
            init_dim, init_dim, kernel_size=2, stride=2, compute_dtype=compute_dtype
        )
        self.block1 = self._make_layer(
            blocks[0], init_dim, planes[0], layers[0], block_kwargs[0], compute_dtype=compute_dtype
        )

        self.conv2 = ConvBlock(
            planes[0], planes[0], kernel_size=2, stride=2, compute_dtype=compute_dtype
        )
        self.block2 = self._make_layer(
            blocks[1], planes[0], planes[1], layers[1], block_kwargs[1], compute_dtype=compute_dtype
        )

        self.conv3 = ConvBlock(
            planes[1], planes[1], kernel_size=2, stride=2, compute_dtype=compute_dtype
        )
        self.block3 = self._make_layer(
            blocks[2], planes[1], planes[2], layers[2], block_kwargs[2], compute_dtype=compute_dtype
        )

        self.conv4 = ConvBlock(
            planes[2], planes[2], kernel_size=2, stride=2, compute_dtype=compute_dtype
        )
        self.block4 = self._make_layer(
            blocks[3], planes[2], planes[3], layers[3], block_kwargs[3], compute_dtype=compute_dtype
        )

        # Upsampling path
        self.convtr4 = ConvTrBlock(
            planes[3], planes[4], kernel_size=2, stride=2, compute_dtype=compute_dtype
        )
        self.block5 = self._make_layer(
            blocks[4],
            planes[4] + planes[2],
            planes[4],
            layers[4],
            block_kwargs[4],
            compute_dtype=compute_dtype,
        )

        self.convtr5 = ConvTrBlock(
            planes[4], planes[5], kernel_size=2, stride=2, compute_dtype=compute_dtype
        )
        self.block6 = self._make_layer(
            blocks[5],
            planes[5] + planes[1],
            planes[5],
            layers[5],
            block_kwargs[5],
            compute_dtype=compute_dtype,
        )

        self.convtr6 = ConvTrBlock(
            planes[5], planes[6], kernel_size=2, stride=2, compute_dtype=compute_dtype
        )
        self.block7 = self._make_layer(
            blocks[6],
            planes[6] + planes[0],
            planes[6],
            layers[6],
            block_kwargs[6],
            compute_dtype=compute_dtype,
        )

        self.convtr7 = ConvTrBlock(
            planes[6], planes[7], kernel_size=2, stride=2, compute_dtype=compute_dtype
        )
        self.block8 = self._make_layer(
            blocks[7],
            planes[7] + planes[0],
            planes[7],
            layers[7],
            block_kwargs[7],
            compute_dtype=compute_dtype,
        )

        # Final convolution
        self.final = SparseConv3d(planes[7], out_channels, kernel_size=1, bias=True)

    def _make_layer(
        self,
        BLOCK: nn.Module,
        in_channels: int,
        out_channels: int,
        blocks: int,
        block_kwargs: dict,
        compute_dtype: Optional[torch.dtype] = None,
    ) -> nn.Sequential:
        layers = []
        layers.append(
            BLOCK(
                in_channels,
                out_channels,
                compute_dtype=compute_dtype,
                **block_kwargs,
            )
        )
        for _ in range(1, blocks):
            layers.append(
                BLOCK(
                    out_channels,
                    out_channels,
                    compute_dtype=compute_dtype,
                    **block_kwargs,
                )
            )
        return nn.Sequential(*layers)

    def forward(self, x: Voxels) -> Voxels:
        # Downsampling path
        out = self.conv0(x)
        out_p1 = out

        out = self.conv1(out_p1)
        out = self.block1(out)
        out_b1p2 = out

        out = self.conv2(out_b1p2)
        out = self.block2(out)
        out_b2p4 = out

        out = self.conv3(out_b2p4)
        out = self.block3(out)
        out_b3p8 = out

        out = self.conv4(out_b3p8)
        out = self.block4(out)

        # Upsampling path
        out = self.convtr4(out, out_b3p8)
        out = cat(out, out_b3p8)
        out = self.block5(out)

        out = self.convtr5(out, out_b2p4)
        out = cat(out, out_b2p4)
        out = self.block6(out)

        out = self.convtr6(out, out_b1p2)
        out = cat(out, out_b1p2)
        out = self.block7(out)

        out = self.convtr7(out, out_p1)
        out = cat(out, out_p1)
        out = self.block8(out)

        return self.final(out)


class MinkUNet18(MinkUNetBase):
    def __init__(self, in_channels: int, out_channels: int, **kwargs):
        super().__init__(
            in_channels,
            out_channels,
            planes=(32, 64, 128, 256, 256, 128, 96, 96),
            layers=(2, 2, 2, 2, 2, 2, 2, 2),
            init_dim=32,
            BLOCK=BasicBlock,
            **kwargs,
        )


class MinkUNet34(MinkUNetBase):
    def __init__(self, in_channels: int, out_channels: int, **kwargs):
        super().__init__(
            in_channels,
            out_channels,
            planes=(32, 64, 128, 256, 256, 128, 96, 96),
            layers=(2, 3, 4, 6, 2, 2, 2, 2),
            init_dim=32,
            BLOCK=BasicBlock,
            **kwargs,
        )


class MinkUNet50(MinkUNetBase):
    def __init__(self, in_channels: int, out_channels: int, **kwargs):
        super().__init__(
            in_channels,
            out_channels,
            planes=(32, 64, 128, 256, 256, 128, 96, 96),
            layers=(2, 3, 4, 6, 2, 2, 2, 2),
            init_dim=32,
            BLOCK=BottleneckBlock,
            **kwargs,
        )


class MinkUNet101(MinkUNetBase):
    def __init__(self, in_channels: int, out_channels: int, **kwargs):
        super().__init__(
            in_channels,
            out_channels,
            planes=(32, 64, 128, 256, 256, 128, 96, 96),
            layers=(2, 3, 4, 23, 2, 2, 2, 2),
            init_dim=32,
            BLOCK=BottleneckBlock,
            **kwargs,
        )


class PointMinkUNetBase(MinkUNetBase):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        planes: tuple[int, ...],
        layers: tuple[int, ...],
        init_dim: int = 32,
        block: nn.Module = ConvBlock,
        voxel_size: float = 0.02,
        **kwargs,
    ):
        super().__init__(
            init_dim,
            planes[-1],
            planes=planes,
            layers=layers,
            init_dim=init_dim,
            block=block,
            **kwargs,
        )

        self.voxel_size = voxel_size
        search_args = RealSearchConfig(
            mode=RealSearchMode.RADIUS,
            radius=voxel_size,
        )
        self.point_conv = PointConv(
            in_channels,
            init_dim,
            hidden_dim=2 * init_dim,
            neighbor_search_args=search_args,
            bias=True,
        )

        self.last_conv = Sequential(
            PointConv(
                planes[-1] + init_dim,
                planes[-1],
                hidden_dim=planes[-1],
                neighbor_search_args=search_args,
                bias=True,
            ),
            nn.BatchNorm1d(planes[-1]),
            nn.ReLU(inplace=True),
            PointConv(
                planes[-1],
                planes[-1],
                hidden_dim=planes[-1],
                neighbor_search_args=search_args,
                bias=True,
            ),
            nn.BatchNorm1d(planes[-1]),
            nn.ReLU(inplace=True),
            nn.Linear(planes[-1], out_channels),
        )

    def forward(self, x: Points) -> Points:
        pc = self.point_conv(x)
        st, to_unique = point_pool(
            pc,
            reduction="mean",
            downsample_voxel_size=self.voxel_size,
            return_type="sparse",
            return_to_unique=True,
        )
        st = super().forward(st)
        final_pc = point_unpool(
            pooled_pc=st.to_point(self.voxel_size),
            unpooled_pc=pc,
            concat_unpooled_pc=True,
            to_unique=to_unique,
        )
        final_pc = self.last_conv(final_pc)
        return final_pc


class PointMinkUNet18(PointMinkUNetBase):
    def __init__(self, in_channels: int, out_channels: int, **kwargs):
        super().__init__(
            in_channels,
            out_channels,
            planes=(32, 64, 128, 256, 256, 128, 96, 96),
            layers=(2, 2, 2, 2, 2, 2, 2, 2),
            init_dim=32,
            **kwargs,
        )


class PointMinkUNet34(PointMinkUNetBase):
    def __init__(self, in_channels: int, out_channels: int, **kwargs):
        super().__init__(
            in_channels,
            out_channels,
            planes=(32, 64, 128, 256, 256, 128, 96, 96),
            layers=(2, 3, 4, 6, 2, 2, 2, 2),
            init_dim=32,
            **kwargs,
        )
