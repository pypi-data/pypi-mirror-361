from collections import OrderedDict
from functools import partial

import torch
import torch.nn as nn
from jaxtyping import Float
from torch import Tensor
from warpconvnet.geometry.types.voxels import Voxels
from warpconvnet.nn.modules.base_module import BaseSpatialModule
from warpconvnet.nn.modules.sequential import Sequential
from warpconvnet.nn.modules.spconv_conv import (
    SparseConv3d,
    SparseInverseConv3d,
    SubMConv3d,
)


def trunc_normal_(tensor, std=0.02):
    return torch.nn.init.trunc_normal_(tensor, std=std)


class BasicBlock(BaseSpatialModule):
    expansion = 1

    def __init__(
        self,
        in_channels,
        embed_channels,
        stride=1,
        norm_fn=None,
        bias=False,
    ):
        super().__init__()

        assert norm_fn is not None

        if in_channels == embed_channels:
            self.proj = Sequential(nn.Identity())
        else:
            self.proj = Sequential(
                SubMConv3d(
                    in_channels, embed_channels, kernel_size=1, bias=False
                ),
                norm_fn(embed_channels),
            )

        self.conv1 = SubMConv3d(
            in_channels,
            embed_channels,
            kernel_size=3,
            bias=bias,
        )
        self.bn1 = norm_fn(embed_channels)
        self.relu = nn.ReLU()
        self.conv2 = SubMConv3d(
            embed_channels,
            embed_channels,
            kernel_size=3,
            bias=bias,
        )
        self.bn2 = norm_fn(embed_channels)

    def forward(self, x: Voxels) -> Voxels:
        residual = x

        out_conv1 = self.conv1(x)
        bn1_features = self.bn1(out_conv1.features)
        relu_features = self.relu(bn1_features)

        out_bn_relu = out_conv1.replace(
            batched_features=relu_features,
        )

        out_conv2 = self.conv2(out_bn_relu)
        bn2_features = self.bn2(out_conv2.features)

        proj_residual = self.proj(residual)

        added_features = bn2_features + proj_residual.features
        final_relu_features = self.relu(added_features)

        out_final = out_conv2.replace(
            batched_features=final_relu_features,
        )
        return out_final


class SpConvTrBlock(BaseSpatialModule):
    def __init__(
        self,
        in_channels,
        out_channels,
        kernel_size=2,
        stride=2,
        norm_fn=None,
        bias=False,
    ):
        super().__init__()
        self.conv_tr = SparseInverseConv3d(
            in_channels,
            out_channels,
            kernel_size=kernel_size,
            stride=stride,
            bias=bias,
        )
        # Norm and ReLU will be applied sequentially after conv_tr
        # Sequential is designed to handle Voxels input and apply BatchNorm1d to features
        self.norm_act = Sequential(
            norm_fn(out_channels),
            nn.ReLU(),
        )

    def forward(self, x: Voxels, output_voxels_sparsity: Voxels) -> Voxels:
        out = self.conv_tr(x, output_voxels=output_voxels_sparsity)
        out = self.norm_act(out)
        return out


class SpUNetBase(nn.Module):
    def __init__(
        self,
        in_channels,
        num_classes,
        base_channels=32,
        channels=(32, 64, 128, 256, 256, 128, 96, 96),
        layers=(2, 3, 4, 6, 2, 2, 2, 2),
        **kwargs,
    ):
        super().__init__()
        assert len(layers) % 2 == 0
        assert len(layers) == len(channels)
        self.in_channels = in_channels
        self.num_classes = num_classes
        self.base_channels = base_channels
        self.channels = channels
        self.layers = layers
        self.num_stages = len(layers) // 2

        norm_fn = partial(nn.BatchNorm1d, eps=1e-3, momentum=0.01)
        block = BasicBlock

        self.conv_input = Sequential(
            SubMConv3d(
                in_channels,
                base_channels,
                kernel_size=5,
                bias=False,
            ),
            norm_fn(base_channels),
            nn.ReLU(),
        )

        enc_channels = base_channels
        dec_channels = channels[-1]
        self.down = nn.ModuleList()
        self.up = nn.ModuleList()
        self.enc = nn.ModuleList()
        self.dec = nn.ModuleList()

        for s in range(self.num_stages):
            self.down.append(
                Sequential(
                    SparseConv3d(
                        enc_channels,
                        channels[s],
                        kernel_size=2,
                        stride=2,
                        bias=False,
                    ),
                    norm_fn(channels[s]),
                    nn.ReLU(),
                )
            )
            self.enc.append(
                Sequential(
                    OrderedDict(
                        [
                            (
                                f"block{i}",
                                block(
                                    channels[s],
                                    channels[s],
                                    norm_fn=norm_fn,
                                ),
                            )
                            for i in range(layers[s])
                        ]
                    )
                )
            )
            self.up.append(
                SpConvTrBlock(
                    in_channels=channels[len(channels) - s - 2],
                    out_channels=dec_channels,
                    kernel_size=2,
                    norm_fn=norm_fn,
                    bias=False,
                )
            )
            self.dec.append(
                Sequential(
                    OrderedDict(
                        [
                            (
                                f"block{i}",
                                block(
                                    # Input channels: concatenation of upsampled and skip for the first block
                                    (
                                        (
                                            dec_channels
                                            + enc_channels
                                        )
                                        if i == 0
                                        else dec_channels
                                    ),
                                    # Output channels for the block
                                    dec_channels,
                                    norm_fn=norm_fn,
                                ),
                            )
                            # Number of layers for this decoder stage, matches spconv_unet_v1m1_base.py
                            for i in range(layers[len(channels) - s - 1])
                        ]
                    )
                )
            )

            enc_channels = channels[s]
            dec_channels = channels[len(channels) - s - 2]

        final_in_channels = channels[-1]
        self.final = (
            SubMConv3d(final_in_channels, num_classes, kernel_size=1, bias=True)
            if num_classes > 0
            else nn.Identity()
        )
        self.apply(self._init_weights)

    @staticmethod
    def _init_weights(m):
        if isinstance(m, nn.Linear):
            trunc_normal_(m.weight, std=0.02)
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)
        elif isinstance(m, (SubMConv3d, SparseConv3d, SparseInverseConv3d)):
            trunc_normal_(m.weight, std=0.02)
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)
        elif isinstance(m, nn.BatchNorm1d):
            nn.init.constant_(m.bias, 0)
            nn.init.constant_(m.weight, 1.0)

    def forward(self, input_voxels: Voxels) -> Float[Tensor, "N C"]:
        if input_voxels.numel() == 0:
            if self.num_classes > 0:
                return torch.empty(
                    (0, self.num_classes), device=input_voxels.device, dtype=input_voxels.dtype
                )
            else:
                return torch.empty(
                    (0, self.in_channels), device=input_voxels.device, dtype=input_voxels.dtype
                )

        x = self.conv_input(input_voxels)

        skips = []
        skips.append(x)

        for s in range(self.num_stages):
            x = self.down[s](x)
            x = self.enc[s](x)
            skips.append(x)

        x = skips.pop(-1)
        for s in reversed(range(self.num_stages)):
            skip_features_voxel = skips.pop(-1)
            x = self.up[s](x, skip_features_voxel)
            x = x.replace(
                batched_features=torch.cat(
                    (x.feature_tensor, skip_features_voxel.feature_tensor), dim=1
                )
            )
            x = self.dec[s](x)

        x = self.final(x)
        return x


class SpUNetNoSkipBase(nn.Module):
    def __init__(
        self,
        in_channels,
        out_channels,
        base_channels=32,
        channels=(32, 64, 128, 256, 256, 128, 96, 96),
        layers=(2, 3, 4, 6, 2, 2, 2, 2),
    ):
        super().__init__()
        assert len(layers) % 2 == 0
        assert len(layers) == len(channels)
        self.in_channels = in_channels
        self.out_channels = out_channels
        self.base_channels = base_channels
        self.channels = channels
        self.layers = layers
        self.num_stages = len(layers) // 2

        self.norm_fn = partial(nn.BatchNorm1d, eps=1e-3, momentum=0.01)
        self.block = BasicBlock

        self.conv_input = Sequential(
            SubMConv3d(
                in_channels,
                base_channels,
                kernel_size=5,
                bias=False,
            ),
            self.norm_fn(base_channels),
            nn.ReLU(),
        )

        enc_channels_current = base_channels
        self.down = nn.ModuleList()
        self.up = nn.ModuleList()
        self.enc = nn.ModuleList()
        self.dec = nn.ModuleList()

        # Encoder
        for s in range(self.num_stages):
            self.down.append(
                Sequential(
                    SparseConv3d(
                        enc_channels_current,
                        channels[s],
                        kernel_size=2,
                        stride=2,
                        bias=False,
                    ),
                    self.norm_fn(channels[s]),
                    nn.ReLU(),
                )
            )
            self.enc.append(
                Sequential(
                    OrderedDict(
                        [
                            (
                                f"block{i}",
                                self.block(
                                    channels[s],
                                    channels[s],
                                    norm_fn=self.norm_fn,
                                ),
                            )
                            for i in range(layers[s])
                        ]
                    )
                )
            )
            enc_channels_current = channels[s]

        # Decoder (No Skip Connections)
        dec_channels_current = channels[self.num_stages - 1]

        for s in range(self.num_stages):
            up_out_channels = channels[self.num_stages + s]
            self.up.append(
                Sequential(
                    SparseInverseConv3d(
                        dec_channels_current,
                        up_out_channels,
                        kernel_size=2,
                        bias=False,
                    ),
                    self.norm_fn(up_out_channels),
                    nn.ReLU(),
                )
            )

            current_block_io_channels = up_out_channels
            self.dec.append(
                Sequential(
                    OrderedDict(
                        [
                            (
                                f"block{i}",
                                self.block(
                                    current_block_io_channels,
                                    current_block_io_channels,
                                    norm_fn=self.norm_fn,
                                ),
                            )
                            for i in range(layers[self.num_stages + s])
                        ]
                    )
                )
            )
            dec_channels_current = current_block_io_channels

        self.final = (
            SubMConv3d(channels[-1], out_channels, kernel_size=1, bias=True)
            if out_channels > 0
            else nn.Identity()
        )
        self.apply(self._init_weights)

    @staticmethod
    def _init_weights(m):
        if isinstance(m, nn.Linear):
            trunc_normal_(m.weight, std=0.02)
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)
        elif isinstance(m, (SubMConv3d, SparseConv3d, SparseInverseConv3d)):
            trunc_normal_(m.weight, std=0.02)
            if m.bias is not None:
                nn.init.constant_(m.bias, 0)
        elif isinstance(m, nn.BatchNorm1d):
            nn.init.constant_(m.bias, 0)
            nn.init.constant_(m.weight, 1.0)

    def forward(self, input_voxels: Voxels):
        if input_voxels.is_empty:
            if self.out_channels > 0:
                return torch.empty(
                    (0, self.out_channels), device=input_voxels.device, dtype=input_voxels.dtype
                )
            else:
                return torch.empty(
                    (0, self.in_channels), device=input_voxels.device, dtype=input_voxels.dtype
                )

        x = self.conv_input(input_voxels)

        # Encoder
        for s in range(self.num_stages):
            x = self.down[s](x)
            x = self.enc[s](x)

        # Decoder (No Skip Connections)
        # x is now the bottleneck features from the encoder
        # Use the self.up and self.dec ModuleLists populated in __init__
        for s in range(self.num_stages):
            x = self.up[s](x)
            x = self.dec[s](x)

        x = self.final(x)
        return x.features.batched_tensor if isinstance(x, Voxels) else x
