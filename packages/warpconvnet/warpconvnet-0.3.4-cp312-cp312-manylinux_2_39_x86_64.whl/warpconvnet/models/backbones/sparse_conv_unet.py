import functools
from typing import Callable, List, Literal, Optional, Tuple, Union

import torch.nn as nn
from warpconvnet.geometry.types.voxels import Voxels
from warpconvnet.nn.functional.transforms import cat
from warpconvnet.nn.modules.activations import ReLU
from warpconvnet.nn.modules.attention import (
    PatchAttention,
    SpatialFeatureAttention,
    TransformerBlock,
)
from warpconvnet.nn.modules.normalizations import BatchNorm
from warpconvnet.nn.modules.sequential import Sequential
from warpconvnet.nn.modules.sparse_conv import SparseConv3d


class ResidualBlock(nn.Module):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        norm_fn: Optional[Callable[[int], nn.Module]] = None,
    ):
        super().__init__()

        if norm_fn is None:
            norm_fn = functools.partial(BatchNorm, eps=1e-4, momentum=0.1)

        if in_channels == out_channels:
            self.i_branch = nn.Identity()
        else:
            self.i_branch = SparseConv3d(
                in_channels, out_channels, kernel_size=1, bias=False
            )

        self.conv_branch = Sequential(
            norm_fn(in_channels),
            nn.ReLU(inplace=True),
            SparseConv3d(in_channels, out_channels, kernel_size=3, bias=False),
            norm_fn(out_channels),
            nn.ReLU(inplace=True),
            SparseConv3d(out_channels, out_channels, kernel_size=3, bias=False),
        )

    def forward(self, x: Voxels) -> Voxels:
        identity = x
        out = self.conv_branch(x)
        out = out + self.i_branch(identity)
        return out


class ResidualTransformerBlock(nn.Module):
    """
    Residual block followed by a transformer block.
    """

    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        num_heads: int,
        qkv_bias: bool = False,
        qk_scale: Optional[float] = None,
        attn_drop: float = 0.0,
        proj_drop: float = 0.0,
        ffn_multiplier: int = 2,
        norm_eps: float = 1e-5,
        norm_fn: Optional[Callable[[int], nn.Module]] = None,
        attn_fn: Optional[
            Callable[[Voxels], Voxels]
        ] = None,
    ):
        super().__init__()
        self.residual = ResidualBlock(in_channels, out_channels, norm_fn)
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


class UBlock(nn.Module):
    def __init__(
        self,
        in_channels: List[int],
        out_channels: List[int],
        norm_fn: Callable[[int], nn.Module],
        num_blocks: int,
        blocks: List[nn.Module],
        block_kwargs: List[dict],
    ):
        """
        Args:
            in_channels: List of input channels for each block. Shallow to deep from left to right.
            out_channels: List of output channels for each block. Shallow to deep from left to right.
            norm_fn: Normalization function.
            num_blocks: Number of blocks in the U-Net.
            blocks: List of block modules for each level.
            block_kwargs: List of kwargs dictionaries for each block type.
        """
        super().__init__()
        self.is_innermost = len(in_channels) == 1

        # Use the first block type and its kwargs for this level
        current_block = blocks[0]
        current_kwargs = block_kwargs[0]

        self.blocks = nn.Sequential(
            *[
                current_block(
                    in_channels[0],
                    out_channels[0] if self.is_innermost else in_channels[0],
                    norm_fn=norm_fn,
                    **current_kwargs,
                )
                for _ in range(num_blocks)
            ]
        )

        if not self.is_innermost:
            self.conv = nn.Sequential(
                norm_fn(in_channels[0]),
                ReLU(inplace=True),
                SparseConv3d(
                    in_channels[0], in_channels[1], kernel_size=2, stride=2, bias=False
                ),
            )

            # Pass remaining blocks and their kwargs to next level
            self.u = UBlock(
                in_channels[1:],
                out_channels[1:],
                norm_fn,
                num_blocks,
                blocks[1:],
                block_kwargs[1:],
            )

            self.deconv_pre = nn.Sequential(
                norm_fn(out_channels[1]),
                ReLU(inplace=True),
            )
            self.deconv = SparseConv3d(
                out_channels[1],
                out_channels[0],
                kernel_size=2,
                stride=2,
                transposed=True,
                bias=False,
            )

            self.blocks_tail = nn.Sequential(
                current_block(
                    out_channels[0] + in_channels[0],
                    out_channels[0],
                    norm_fn=norm_fn,
                    **current_kwargs,
                ),
                *[
                    current_block(
                        out_channels[0],
                        out_channels[0],
                        norm_fn=norm_fn,
                        **current_kwargs,
                    )
                    for i in range(num_blocks - 1)
                ],
            )

    def forward(self, x: Voxels) -> Tuple[Voxels, ...]:
        output = self.blocks(x)
        if self.is_innermost:
            return [output]

        identity = output
        output = self.conv(output)
        u_outs = self.u(output)
        output_decoder = self.deconv_pre(u_outs[0])
        output_decoder = self.deconv(output_decoder, identity)
        output = cat(identity, output_decoder)
        output = self.blocks_tail(output)
        return output, *u_outs


class SparseConvUNet(nn.Module):
    def __init__(
        self,
        in_channels: int,
        enc_channels: List[int],
        dec_channels: List[int],
        num_blocks: int,
        out_channels: Optional[int] = None,
        return_intermediate: bool = False,
        block_types: Union[str, List[Literal["res", "attn", "pattn"]]] = "res",
        num_heads: Optional[List[int]] = None,
        patch_sizes: Union[int, List[int]] = 1024,
        **kwargs,
    ):
        """
        Args:
            in_channels: Input channel.
            enc_channels: List of input channels for each block. Shallow to deep from left to right.
            dec_channels: List of output channels for each block. Shallow to deep from left to right.
            num_blocks: Number of blocks in the U-Net.
            out_channels: Optional output channel.
            return_intermediate: Whether to return intermediate features.
            block_types: Type of block to use ("residual" or "attention") or list of types for each level.
            num_heads: Number of attention heads when using attention blocks.
        """
        super().__init__()
        self.return_intermediate = return_intermediate
        norm_fn = functools.partial(BatchNorm, eps=1e-4, momentum=0.1)

        # Convert single block type to list if needed
        if isinstance(block_types, str):
            block_types = [block_types] * len(enc_channels)
        if isinstance(patch_sizes, int):
            patch_sizes = [patch_sizes] * len(enc_channels)

        assert len(block_types) == len(enc_channels)
        assert len(enc_channels) == len(dec_channels)

        # Create lists of block modules and their kwargs
        blocks = []
        block_kwargs = []
        for i, block_type in enumerate(block_types):
            assert block_type in ["res", "attn", "pattn"]
            if block_type == "res":
                blocks.append(ResidualBlock)
                block_kwargs.append({})
            elif block_type == "attn":
                assert num_heads is not None
                assert len(num_heads) == len(enc_channels)
                blocks.append(ResidualTransformerBlock)
                block_kwargs.append(
                    {
                        "num_heads": num_heads[i],
                        "attn_fn": functools.partial(
                            SpatialFeatureAttention,
                            use_encoding=False,
                        ),
                    }
                )
            elif block_type == "pattn":
                assert num_heads is not None
                assert len(num_heads) == len(enc_channels)
                assert len(patch_sizes) == len(enc_channels)
                blocks.append(ResidualTransformerBlock)
                block_kwargs.append(
                    {
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

        self.input_conv = SparseConv3d(
            in_channels, enc_channels[0], kernel_size=3, bias=False
        )

        self.unet = UBlock(
            enc_channels,
            dec_channels,
            norm_fn=norm_fn,
            num_blocks=num_blocks,
            blocks=blocks,
            block_kwargs=block_kwargs,
        )

        self.output_layer = nn.Sequential(
            norm_fn(dec_channels[0]),
            ReLU(inplace=True),
            (
                SparseConv3d(dec_channels[0], out_channels, kernel_size=1, bias=False)
                if out_channels is not None
                else nn.Identity()
            ),
        )

    def forward(self, x: Voxels) -> Voxels:
        output = self.input_conv(x)
        decoder_outs = self.unet(output)
        output = self.output_layer(decoder_outs[0])
        if self.return_intermediate:
            return output, *decoder_outs[1:]
        return output
