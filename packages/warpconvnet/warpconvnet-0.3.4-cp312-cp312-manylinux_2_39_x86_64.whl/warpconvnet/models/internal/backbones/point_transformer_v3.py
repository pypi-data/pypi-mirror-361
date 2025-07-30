# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
import random
import unittest
from typing import Literal, Optional, Tuple

import torch
import torch.nn as nn
import warp as wp
from jaxtyping import Float, Int

try:
    import flash_attn
except ImportError:
    flash_attn = None

from warpconvnet.geometry.base.geometry import Geometry
from warpconvnet.geometry.coords.ops.serialization import POINT_ORDERING
from warpconvnet.geometry.types.conversion.to_voxels import points_to_voxels
from warpconvnet.geometry.types.points import Points
from warpconvnet.geometry.types.voxels import Voxels
from warpconvnet.models.internal.backbones.components.voxel_encode import (
    STR2COORD_OFFSET,
    voxel_encode,
)
from warpconvnet.models.internal.backbones.components.window_attention import (
    VoxelPatchAttention,
    WindowAttention,
)
from warpconvnet.nn.modules.activations import GELU, DropPath
from warpconvnet.nn.modules.attention import FeedForward, PatchAttention
from warpconvnet.nn.modules.base_module import BaseSpatialModel, BaseSpatialModule
from warpconvnet.nn.modules.mlp import Linear
from warpconvnet.nn.modules.normalizations import LayerNorm
from warpconvnet.nn.modules.sequential import Sequential, TupleSequential
from warpconvnet.nn.modules.sparse_conv import SparseConv3d
from warpconvnet.nn.modules.sparse_pool import SparseMaxPool, SparseUnpool

STR2ATTN = {
    "patch": PatchAttention,
    "window": WindowAttention,
    "voxel": VoxelPatchAttention,
}


class AttentionBlock(BaseSpatialModule):
    def __init__(
        self,
        in_channels: int,
        attention_channels: int,
        patch_size: int,
        num_heads: int,
        mlp_ratio: float = 4.0,
        qkv_bias: bool = True,
        qk_scale: Optional[float] = None,
        attn_drop: float = 0.0,
        proj_drop: float = 0.0,
        drop_path: float = 0.0,
        norm_layer: type = LayerNorm,
        act_layer: type = GELU,
        attn_type: Literal["patch", "window", "voxel"] = "patch",
        order: POINT_ORDERING = POINT_ORDERING.RANDOM,
    ):
        super().__init__()
        self.order = order
        assert attn_type in STR2ATTN.keys(), f"Invalid attention type: {attn_type}"
        attn_block = STR2ATTN[attn_type]
        self.conv = Sequential(
            SparseConv3d(
                in_channels,
                in_channels,
                kernel_size=3,
                stride=1,
                bias=True,
            ),
            nn.Linear(in_channels, attention_channels),
            norm_layer(attention_channels),
        )
        self.conv_shortcut = (
            nn.Identity()
            if in_channels == attention_channels
            else Linear(in_channels, attention_channels)
        )

        self.norm1 = norm_layer(attention_channels)
        self.attention = attn_block(
            attention_channels,
            patch_size=patch_size,
            num_heads=num_heads,
            qkv_bias=qkv_bias,
            qk_scale=qk_scale,
            attn_drop=attn_drop,
            proj_drop=proj_drop,
            order=order,
        )
        self.norm2 = norm_layer(attention_channels)
        self.mlp = FeedForward(
            dim=attention_channels,
            hidden_dim=int(attention_channels * mlp_ratio),
        )
        self.drop_path = DropPath(drop_path) if drop_path > 0.0 else nn.Identity()

    def forward(self, x: Geometry, order: Optional[POINT_ORDERING | str] = None) -> Geometry:
        x = self.conv(x) + self.conv_shortcut(x)

        # Attention block
        x = self.norm1(x)
        x = self.drop_path(self.attention(x, order)) + x

        # MLP block
        x = self.norm2(x)
        x = self.drop_path(self.mlp(x)) + x
        return x


class AttentionBlockPeriLN(BaseSpatialModule):
    def __init__(
        self,
        in_channels: int,
        attention_channels: int,
        patch_size: int,
        num_heads: int,
        mlp_ratio: float = 4.0,
        qkv_bias: bool = True,
        qk_scale: Optional[float] = None,
        attn_drop: float = 0.0,
        proj_drop: float = 0.0,
        drop_path: float = 0.0,
        norm_layer: type = LayerNorm,
        attn_type: Literal["patch", "window", "voxel"] = "patch",
        order: POINT_ORDERING = POINT_ORDERING.RANDOM,
    ):
        super().__init__()
        self.order = order
        assert attn_type in STR2ATTN.keys(), f"Invalid attention type: {attn_type}"
        attn_block = STR2ATTN[attn_type]
        self.conv = Sequential(
            SparseConv3d(
                in_channels,
                in_channels,
                kernel_size=3,
                stride=1,
                bias=True,
            ),
            nn.Linear(in_channels, attention_channels),
            norm_layer(attention_channels),
        )
        self.conv_shortcut = (
            nn.Identity()
            if in_channels == attention_channels
            else Linear(in_channels, attention_channels)
        )

        self.attn_norm_pre = norm_layer(attention_channels)
        self.attention = attn_block(
            attention_channels,
            patch_size=patch_size,
            num_heads=num_heads,
            qkv_bias=qkv_bias,
            qk_scale=qk_scale,
            attn_drop=attn_drop,
            proj_drop=proj_drop,
            order=order,
        )
        self.attn_norm_post = norm_layer(attention_channels)

        # Peri-LN MLP block
        self.mlp_block = Sequential(
            norm_layer(attention_channels),
            FeedForward(
                dim=attention_channels,
                hidden_dim=int(attention_channels * mlp_ratio),
            ),
            DropPath(drop_path) if drop_path > 0.0 else nn.Identity(),
            norm_layer(attention_channels),
        )

    def forward(self, x: Geometry, order: Optional[POINT_ORDERING | str] = None) -> Geometry:
        x = self.conv(x) + self.conv_shortcut(x)

        # Attention block (Peri-LN)
        x = self.attn_norm_post(self.attention(self.attn_norm_pre(x), order)) + x

        # MLP block
        x = self.mlp_block(x) + x
        return x


STR2BLOCK = {
    "pre_ln": AttentionBlock,
    "peri_ln": AttentionBlockPeriLN,
}


class PointTransformerV3(BaseSpatialModel):
    def __init__(
        self,
        in_channels: int = 6,
        enc_depths: Tuple[int, ...] = (2, 2, 2, 6, 2),
        enc_channels: Tuple[int, ...] = (32, 64, 128, 256, 512),
        enc_num_head: Tuple[int, ...] = (2, 4, 8, 16, 32),
        enc_patch_size: Tuple[int, ...] = (1024, 1024, 1024, 1024, 1024),
        dec_depths: Tuple[int, ...] = (2, 2, 2, 2),
        dec_channels: Tuple[int, ...] = (64, 64, 128, 256),
        dec_num_head: Tuple[int, ...] = (4, 4, 8, 16),
        dec_patch_size: Tuple[int, ...] = (1024, 1024, 1024, 1024),
        mlp_ratio: float = 4,
        qkv_bias: bool = True,
        qk_scale: Optional[float] = None,
        attn_drop: float = 0.0,
        proj_drop: float = 0.0,
        drop_path: float = 0.2,
        orders: Tuple[POINT_ORDERING, ...] = tuple(POINT_ORDERING),
        shuffle_orders: bool = True,
        block_type: Literal["pre_ln", "peri_ln"] = "pre_ln",
        attn_type: Literal["patch", "window", "voxel"] = "patch",
        **kwargs,
    ):
        super().__init__()

        num_level = len(enc_depths)
        assert num_level == len(enc_channels)
        assert num_level == len(enc_num_head)
        assert num_level == len(enc_patch_size)

        assert num_level - 1 == len(dec_channels)
        assert num_level - 1 == len(dec_depths)
        assert num_level - 1 == len(dec_num_head)
        assert num_level - 1 == len(dec_patch_size)
        self.num_level = num_level
        self.shuffle_orders = shuffle_orders
        self.orders = orders
        assert block_type in STR2BLOCK.keys(), f"Invalid block type: {block_type}"
        assert attn_type in STR2ATTN.keys(), f"Invalid attention type: {attn_type}"
        attn_block = STR2BLOCK[block_type]

        self.conv = Sequential(
            SparseConv3d(
                in_channels,
                enc_channels[0],
                kernel_size=5,
            ),
            nn.BatchNorm1d(enc_channels[0]),
            nn.GELU(),
        )

        encs = nn.ModuleList()
        down_convs = nn.ModuleList()
        for i in range(num_level):
            level_blocks = nn.ModuleList(
                [
                    attn_block(
                        in_channels=enc_channels[i],
                        attention_channels=enc_channels[i],
                        patch_size=enc_patch_size[i],
                        num_heads=enc_num_head[i],
                        mlp_ratio=mlp_ratio,
                        qkv_bias=qkv_bias,
                        qk_scale=qk_scale,
                        attn_drop=attn_drop,
                        proj_drop=proj_drop,
                        drop_path=drop_path,
                        order=self.orders[i % len(self.orders)],
                        attn_type=attn_type,
                    )
                    for _ in range(enc_depths[i])
                ]
            )
            encs.append(level_blocks)

            if i < num_level - 1:
                down_convs.append(
                    Sequential(
                        nn.Linear(enc_channels[i], enc_channels[i + 1]),
                        SparseMaxPool(
                            kernel_size=2,
                            stride=2,
                        ),
                        nn.BatchNorm1d(enc_channels[i + 1]),
                        nn.GELU(),
                    )
                )

        decs = nn.ModuleList()
        up_convs = nn.ModuleList()
        dec_channels_list = list(dec_channels) + [enc_channels[-1]]
        for i in reversed(range(num_level - 1)):
            up_convs.append(
                TupleSequential(
                    nn.Linear(dec_channels_list[i + 1], dec_channels_list[i]),
                    SparseUnpool(
                        kernel_size=2,
                        stride=2,
                        concat_unpooled_st=True,
                    ),
                    nn.Linear(dec_channels_list[i] + enc_channels[i], dec_channels_list[i]),
                    nn.BatchNorm1d(dec_channels_list[i]),
                    nn.GELU(),
                    tuple_layer=1,
                )
            )
            level_blocks = nn.ModuleList(
                [
                    attn_block(
                        in_channels=dec_channels_list[i],
                        attention_channels=dec_channels_list[i],
                        patch_size=dec_patch_size[i],
                        num_heads=dec_num_head[i],
                        mlp_ratio=mlp_ratio,
                        qkv_bias=qkv_bias,
                        qk_scale=qk_scale,
                        attn_drop=attn_drop,
                        proj_drop=proj_drop,
                        drop_path=drop_path,
                        order=self.orders[i % len(self.orders)],
                        attn_type=attn_type,
                    )
                    for _ in range(dec_depths[i])
                ]
            )
            decs.append(level_blocks)

        self.encs = encs
        self.down_convs = down_convs
        self.decs = decs
        self.up_convs = up_convs

        out_channels = kwargs.get("out_channels")
        if out_channels is not None:
            self.out_channels = out_channels
            self.final = Linear(dec_channels_list[0], out_channels)
        else:
            self.final = nn.Identity()

    def forward(self, x: Geometry) -> Geometry:
        x = self.conv(x)
        skips = []

        # Encoder
        for level in range(self.num_level):
            # Randomly select an order for this level
            selected_order = (
                random.choice(self.orders)
                if self.shuffle_orders
                else self.orders[level % len(self.orders)]
            )

            # Process each block individually in this level
            level_blocks = self.encs[level]
            for block in level_blocks.children():
                x = block(x, selected_order)

            if level < self.num_level - 1:
                skips.append(x)
                x = self.down_convs[level](x)

        # Decoder
        for level in range(self.num_level - 1):
            x = self.up_convs[level](x, skips[-(level + 1)])

            # Randomly select an order for this level
            selected_order = (
                random.choice(self.orders)
                if self.shuffle_orders
                else self.orders[level % len(self.orders)]
            )

            # Process each block individually in this level
            level_blocks = self.decs[level]
            for block in level_blocks.children():
                x = block(x, selected_order)

        return self.final(x)


class TestAttention(unittest.TestCase):
    def setUp(self):
        wp.init()
        self.B, min_N, max_N, self.C = 3, 1000, 10000, 128
        self.Ns = [N.item() for N in torch.randint(min_N, max_N, (self.B,))]
        self.coords = [torch.rand((N, 3)) for N in self.Ns]
        self.features = [torch.rand((N, self.C)) for N in self.Ns]
        self.pc = Points(self.coords, self.features)

    def test_patch_attention(self):
        device = torch.device("cuda:0")
        pc = self.pc.to(device)
        patch_size = 32
        dim = self.C * 8
        num_heads = 8
        lift = Linear(self.C, dim).to(device)
        patch_attn = PatchAttention(
            dim=dim,
            patch_size=patch_size,
            num_heads=num_heads,
            qkv_bias=True,
        ).to(device)

        pc = lift(pc)
        out = patch_attn(pc)

        self.assertIsInstance(out, Points)
        self.assertEqual(out.feature_tensor.shape[-1], dim)

        # Check that the number of points is preserved
        self.assertEqual(len(out), len(pc))

    def test_patch_attention_block(self):
        device = torch.device("cuda:0")
        pc = self.pc.to(device)
        patch_size = 32
        dim = self.C * 8
        num_heads = 8
        patch_attn = AttentionBlock(
            in_channels=self.C,
            attention_channels=dim,
            patch_size=patch_size,
            num_heads=num_heads,
            mlp_ratio=4,
            qkv_bias=True,
            proj_drop=0.3,
            drop_path=0.3,
            attn_type="patch",
        ).to(device)
        st = points_to_voxels(pc, voxel_size=0.02)
        out = patch_attn(st)
        self.assertEqual(out.feature_tensor.shape[-1], dim)
        self.assertEqual(len(out), len(st))

    def test_point_transformer_v3(self):
        device = torch.device("cuda:0")
        pc = self.pc.to(device)
        pt = PointTransformerV3(
            in_channels=self.C,
            enc_depths=(3, 3, 3, 6, 3),
            enc_channels=(48, 96, 192, 384, 512),
            enc_num_head=(3, 6, 12, 24, 32),
            enc_patch_size=(1024, 1024, 1024, 1024, 1024),
            dec_depths=(3, 3, 3, 3),
            dec_channels=(48, 96, 192, 384),
            dec_num_head=(4, 6, 12, 24),
            dec_patch_size=(1024, 1024, 1024, 1024),
            shuffle_orders=True,
            attn_type="window",
            block_type="pre_ln",
        ).to(device)
        st = points_to_voxels(pc, voxel_size=0.02)
        out = pt(st)
        self.assertIsInstance(out, Voxels)
        self.assertEqual(out.feature_tensor.shape[-1], 48)


if __name__ == "__main__":
    unittest.main()
