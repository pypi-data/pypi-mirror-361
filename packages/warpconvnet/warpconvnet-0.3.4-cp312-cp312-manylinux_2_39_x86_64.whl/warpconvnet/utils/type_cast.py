# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

import torch


# Type casting order.
TYPE_ORDER = [torch.bfloat16, torch.float16, torch.float32, torch.float64]


def _min_dtype(*dtypes):
    assert all(dtype in TYPE_ORDER for dtype in dtypes), f"Invalid dtype: {dtypes}"
    return TYPE_ORDER[min(TYPE_ORDER.index(dtype) for dtype in dtypes)]


def _max_dtype(*dtypes):
    assert all(dtype in TYPE_ORDER for dtype in dtypes), f"Invalid dtype: {dtypes}"
    return TYPE_ORDER[max(TYPE_ORDER.index(dtype) for dtype in dtypes)]
