# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from jaxtyping import Int
from torch import Tensor


def _int_tensor_hash(arr: Int[Tensor, "N"]) -> int:  # noqa: F821
    arr = arr.tolist()
    x = hash(arr[0])
    for i in range(1, len(arr)):
        x = x * 31 + hash(arr[i])
    return x
