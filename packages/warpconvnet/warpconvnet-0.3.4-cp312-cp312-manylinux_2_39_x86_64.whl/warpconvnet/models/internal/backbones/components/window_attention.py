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
from typing import Optional, Tuple, Union

import numpy as np
import torch
import torch.nn as nn
from jaxtyping import Float, Int
from torch import Tensor

try:
    import flash_attn
except ImportError:
    flash_attn = None

from warpconvnet.geometry.base.geometry import Geometry
from warpconvnet.geometry.coords.ops.serialization import (
    POINT_ORDERING,
    SerializationResult,
    encode,
)
from warpconvnet.models.internal.backbones.components.voxel_encode import (
    STR2COORD_OFFSET,
    voxel_encode,
)
from warpconvnet.nn.modules.base_module import BaseSpatialModule


class WindowAttention(BaseSpatialModule):
    def __init__(
        self,
        dim: int,
        window_size: Optional[int] = None,
        num_heads: int = 8,
        qkv_bias: bool = False,
        qk_scale: Optional[float] = None,
        attn_drop: float = 0.0,
        proj_drop: float = 0.0,
        order: POINT_ORDERING = POINT_ORDERING.MORTON_XYZ,
        **kwargs,
    ):
        super().__init__()
        # If patch_size is provided, use it as window_size
        if "patch_size" in kwargs and window_size is None:
            window_size = kwargs["patch_size"]
            del kwargs["patch_size"]
        assert window_size is not None, "window_size must be provided"
        self.window_size = window_size
        self.num_heads = num_heads
        assert dim % num_heads == 0, "dim must be divisible by num_heads"
        head_dim = dim // num_heads
        self.scale = qk_scale or head_dim**-0.5
        self.qkv = nn.Linear(dim, dim * 3, bias=qkv_bias)
        self.order = order
        assert flash_attn is not None, "Make sure flash_attn is installed."
        self.attn_drop_p = attn_drop

        self.proj = nn.Linear(dim, dim)
        self.proj_drop = nn.Dropout(proj_drop)

    def forward(self, x: Geometry, order: Optional[POINT_ORDERING] = None) -> Geometry:
        feats = x.features
        M, C = feats.shape[:2]
        inverse_perm = None
        order = order or self.order
        if not hasattr(x, "order") or (order != x.order):
            # Generate new ordering and inverse permutation
            code_result: SerializationResult = encode(
                x.coordinate_tensor,
                batch_offsets=x.offsets,
                order=order,
                return_perm=True,
                return_inverse=True,
            )
            feats = feats[code_result.perm]
            inverse_perm = code_result.inverse_perm

        # Flash attention path - use variable length version for patches
        # Reshape for flash attention: (M, 3, num_heads, head_dim)
        qkv = self.qkv(feats)
        qkv = qkv.reshape(-1, 3, self.num_heads, C // self.num_heads)

        # Calculate the maximum sequence length within the batch
        # x.offsets is [0, N_1, N_1 + N_2, ..., sum(N_i)]
        seq_len = x.offsets.diff()
        max_seqlen = seq_len.max().item()

        if qkv.dtype not in [torch.float16, torch.bfloat16]:
            qkv = qkv.to(torch.float16)

        out_feat = flash_attn.flash_attn_varlen_qkvpacked_func(
            qkv,
            x.offsets.to(qkv.device),
            max_seqlen=max_seqlen,
            window_size=(-self.window_size // 2, self.window_size // 2),
            dropout_p=self.attn_drop_p if self.training else 0.0,
            softmax_scale=self.scale,
        )
        out_feat = out_feat.reshape(M, C).to(feats.dtype)

        out_feat = self.proj(out_feat)
        out_feat = self.proj_drop(out_feat)

        if inverse_perm is not None:
            out_feat = out_feat[inverse_perm]

        return x.replace(batched_features=out_feat.to(feats.dtype))


class VoxelPatchAttention(BaseSpatialModule):
    def __init__(
        self,
        dim: int,
        window_size: Optional[Tuple[int, int, int]] = None,
        num_heads: int = 8,
        qkv_bias: bool = False,
        qk_scale: Optional[float] = None,
        attn_drop: float = 0.0,
        proj_drop: float = 0.0,
        offset: Union[str, Tuple[float, float, float]] = "zero",
        **kwargs,
    ):
        super().__init__()
        if "patch_size" in kwargs and window_size is None:
            window_size = kwargs["patch_size"]
            del kwargs["patch_size"]

        if isinstance(window_size, str):
            assert window_size == "all", f"Invalid window_size: {window_size}"

        if isinstance(window_size, int):
            window_size = (window_size, window_size, window_size)

        self.window_size = window_size
        self.num_heads = num_heads
        assert dim % num_heads == 0, "dim must be divisible by num_heads"
        head_dim = dim // num_heads
        self.scale = qk_scale or head_dim**-0.5
        self.qkv = nn.Linear(dim, dim * 3, bias=qkv_bias)
        self.offset = offset
        assert flash_attn is not None, "Make sure flash_attn is installed."
        self.attn_drop_p = attn_drop

        self.proj = nn.Linear(dim, dim)
        self.proj_drop = nn.Dropout(proj_drop)

    def _attn_offset(self, counts: Int[Tensor, "N"]) -> Int[Tensor, "B"]:  # noqa: F821
        result_middle = torch.cumsum(counts, dim=0)
        # Add the final offset
        result = torch.cat([torch.zeros(1, device=counts.device, dtype=counts.dtype), result_middle]).int()
        return result.contiguous()

    def forward(
        self, x: Geometry, coord_offset: Union[Tuple[float, float, float], str] = "zero"
    ) -> Geometry:
        if coord_offset is None:
            coord_offset = self.offset
        if isinstance(coord_offset, str):
            coord_offset = STR2COORD_OFFSET[coord_offset]
        assert (
            isinstance(coord_offset, tuple) and len(coord_offset) == 3
        ), "coord_offset must be a tuple of 3 floats"
        # Assert that x is serialized
        feats = x.features
        M, C = feats.shape[:2]
        code_result = None
        if self.window_size == "all":
            attn_offsets = x.offsets.to(feats.device)
            max_seqlen = x.offsets.diff().max().item()
        else:
            code_result = voxel_encode(
                x.coordinate_tensor,
                batch_offsets=x.offsets,
                coord_offset=coord_offset,
                window_size=self.window_size,
                return_perm=True,
                return_inverse=True,
                return_counts=True,
            )
            feats = feats[code_result.perm]
            attn_offsets = self._attn_offset(code_result.counts).to(feats.device)

            max_seqlen = code_result.counts.max().item()
        # Flash attention path - use variable length version for patches
        # Reshape for flash attention: (M, 3, num_heads, head_dim)
        qkv = self.qkv(feats)
        qkv = qkv.reshape(-1, 3, self.num_heads, C // self.num_heads)
        if qkv.dtype not in [torch.float16, torch.bfloat16]:
            qkv = qkv.to(torch.float16)

        # Warning: When the loss is NaN, this module will fail during backward with
        # index out of bounds error.
        # e.g. /pytorch/aten/src/ATen/native/cuda/ScatterGatherKernel.cu:144: operator(): block: [192,0,0], thread: [32,0,0] Assertion `idx_dim >= 0 && idx_dim < index_size && "
        # https://discuss.pytorch.org/t/scattergatherkernel-cu-assertion-idx-dim-0-idx-dim-index-size-index-out-of-bounds/195356
        out_feat = flash_attn.flash_attn_varlen_qkvpacked_func(
            qkv,
            attn_offsets,
            max_seqlen=max_seqlen,
            dropout_p=self.attn_drop_p if self.training else 0.0,
            softmax_scale=self.scale,
        )
        out_feat = out_feat.reshape(M, C).to(feats.dtype)

        out_feat = self.proj(out_feat)
        out_feat = self.proj_drop(out_feat)

        if code_result is not None:
            out_feat = out_feat[code_result.inverse_perm]

        return x.replace(batched_features=out_feat.to(feats.dtype))
