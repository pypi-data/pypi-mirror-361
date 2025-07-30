from typing import List, Type

import torch.nn as nn
from warpconvnet.models.internal.backbones.components.mink_conv_block import (
    BasicBlockBase,
    get_basic_block,
    get_conv_block,
    tensor_concat,
)


class MinkUNetEncoder(nn.Module):
    def __init__(
        self,
        in_channels: int,
        encoder_channels: List[int],
        num_blocks_per_level: List[int],
        block_types: List[str],
        initial_kernel_size: int = 5,
        bias: bool = False,
    ):
        super().__init__()

        # Length checks
        num_levels = len(encoder_channels) - 1
        if len(encoder_channels) < 2:
            raise ValueError(
                "encoder_channels must contain at least two elements (input and output channels)"
            )
        if len(num_blocks_per_level) != num_levels:
            raise ValueError(
                f"num_blocks_per_level should have {num_levels} elements, "
                f"but got {len(num_blocks_per_level)}"
            )
        if len(block_types) != len(encoder_channels):
            raise ValueError(
                f"block_types should have {len(encoder_channels)} elements, "
                f"but got {len(block_types)}"
            )

        self.blocks = nn.ModuleList()
        self.block_types = block_types

        # Initial convolution
        ConvBlockClass = get_conv_block(block_types[0])
        self.conv0 = ConvBlockClass(
            in_channels,
            encoder_channels[0],
            kernel_size=initial_kernel_size,
            stride=1,
            bias=bias,
        )

        in_ch = encoder_channels[0]
        num_levels = len(num_blocks_per_level)
        for idx in range(num_levels):
            out_ch = encoder_channels[idx + 1]
            block_type = block_types[idx + 1]
            ConvBlockClass = get_conv_block(block_type)
            BasicBlockClass = get_basic_block(block_type)

            conv = ConvBlockClass(
                in_ch,
                out_ch,
                kernel_size=2,
                stride=2,
                bias=bias,
            )
            block_layers = self._make_layer(
                BasicBlockClass,
                out_ch,
                out_ch,
                num_blocks_per_level[idx],
                bias,
            )
            self.blocks.append(nn.Sequential(conv, block_layers))
            in_ch = out_ch

    def _make_layer(
        self,
        block: Type[BasicBlockBase],
        in_channels: int,
        out_channels: int,
        num_blocks: int,
        bias: bool,
    ) -> nn.Sequential:
        layers = [block(in_channels, out_channels, bias=bias)]
        for _ in range(1, num_blocks):
            layers.append(block(out_channels, out_channels, bias=bias))
        return nn.Sequential(*layers)

    def forward(self, x):
        outputs = []
        x = self.conv0(x)
        outputs.append(x)
        for block in self.blocks:
            x = block(x)
            outputs.append(x)
        return outputs  # List of features per level


class MinkUNetDecoder(nn.Module):
    def __init__(
        self,
        decoder_channels: List[int],
        encoder_channels: List[int],
        num_blocks_per_level: List[int],
        block_types: List[str],
        bias: bool = False,
    ):
        super().__init__()

        # Length checks
        num_levels = len(num_blocks_per_level)

        if len(decoder_channels) != num_levels + 1:
            raise ValueError(
                f"decoder_channels should have {num_levels + 1} elements, "
                f"but got {len(decoder_channels)}"
            )
        if len(block_types) != num_levels:
            raise ValueError(
                f"block_types should have {num_levels} elements, but got {len(block_types)}"
            )
        if len(encoder_channels) < num_levels + 1:
            raise ValueError(
                f"encoder_channels should have at least {num_levels + 1} elements, "
                f"but got {len(encoder_channels)}"
            )

        self.blocks = nn.ModuleList()
        self.block_types = block_types

        num_levels = len(num_blocks_per_level)
        for idx in range(num_levels):
            in_ch = decoder_channels[idx]
            out_ch = decoder_channels[idx + 1]
            skip_ch = encoder_channels[-(idx + 2)]  # Corresponding skip connection channels
            total_in_ch = out_ch + skip_ch

            block_type = block_types[idx]
            ConvBlockClass = get_conv_block(block_type)
            BasicBlockClass = get_basic_block(block_type)

            convtr = ConvBlockClass(
                in_ch,
                out_ch,
                kernel_size=2,
                stride=2,
                transposed=True,
                bias=bias,
            )
            block_layers = self._make_layer(
                BasicBlockClass,
                total_in_ch,
                out_ch,
                num_blocks_per_level[idx],
                bias,
            )
            self.blocks.append(nn.Sequential(convtr, block_layers))

    def _make_layer(
        self,
        block: Type[BasicBlockBase],
        in_channels: int,
        out_channels: int,
        num_blocks: int,
        bias: bool,
    ) -> nn.Sequential:
        layers = [block(in_channels, out_channels, bias=bias)]
        for _ in range(1, num_blocks):
            layers.append(block(out_channels, out_channels, bias=bias))
        return nn.Sequential(*layers)

    def forward(self, encoder_outputs: List):
        x = encoder_outputs[-1]  # Start from the deepest encoder output
        for idx, block in enumerate(self.blocks):
            # Get the corresponding skip connection
            skip = encoder_outputs[-(idx + 2)]

            prev_st = encoder_outputs[-(idx + 1)] if idx > 0 else None
            # Transposed convolution
            x = block[0](
                x,
                from_dense_spatial_sparsity=prev_st,
                transposed_out_spatial_sparsity=skip,
            )

            # Concatenate skip features
            x = self._concat(x, skip)

            x = block[1](x)  # BasicBlock
        return x

    def _concat(self, x, skip):
        return tensor_concat(x, skip)


class MinkSparseDenseUNet(nn.Module):
    def __init__(
        self,
        in_channels: int,
        out_channels: int,
        encoder_channels: List[int],
        decoder_channels: List[int],
        encoder_blocks: List[int],
        decoder_blocks: List[int],
        dense_depth: int,
        initial_kernel_size: int = 5,
        final_kernel_size: int = 1,
        bias: bool = False,
    ):
        super().__init__()

        # Validation checks
        num_encoder_levels = len(encoder_channels) - 1
        num_decoder_levels = len(decoder_blocks)

        if dense_depth < 0 or dense_depth > num_encoder_levels:
            raise ValueError(
                f"dense_depth must be between 0 and {num_encoder_levels}, but got {dense_depth}"
            )

        # Compute encoder block types based on dense_depth
        encoder_block_types = ['sparse'] * (dense_depth + 1) + ['dense'] * (num_encoder_levels - dense_depth)
        # The initial block is considered level 0, so we add 1 to dense_depth for encoder_block_types

        # Compute decoder block types based on dense_depth
        decoder_block_types = ['dense'] * (num_encoder_levels - dense_depth) + ['sparse'] * dense_depth

        # Ensure lengths match
        assert len(encoder_block_types) == len(encoder_channels), \
            f"encoder_block_types length {len(encoder_block_types)} does not match encoder_channels length {len(encoder_channels)}"
        assert len(decoder_block_types) == num_decoder_levels, \
            f"decoder_block_types length {len(decoder_block_types)} does not match the number of decoder levels {num_decoder_levels}"

        # Initialize encoder and decoder
        self.encoder = MinkUNetEncoder(
            in_channels=in_channels,
            encoder_channels=encoder_channels,
            num_blocks_per_level=encoder_blocks,
            block_types=encoder_block_types,
            initial_kernel_size=initial_kernel_size,
            bias=bias,
        )

        self.decoder = MinkUNetDecoder(
            decoder_channels=decoder_channels,
            encoder_channels=encoder_channels,
            num_blocks_per_level=decoder_blocks,
            block_types=decoder_block_types,
            bias=bias,
        )

        # Final convolution layer
        final_block_type = decoder_block_types[-1]
        ConvBlockClass = get_conv_block(final_block_type)
        self.final = ConvBlockClass(
            decoder_channels[-1],
            out_channels,
            kernel_size=final_kernel_size,
            stride=1,
            bias=bias,
            activation=None,
        )

    def forward(self, x):
        encoder_outputs = self.encoder(x)
        out = self.decoder(encoder_outputs)
        out = self.final(out)
        return out
