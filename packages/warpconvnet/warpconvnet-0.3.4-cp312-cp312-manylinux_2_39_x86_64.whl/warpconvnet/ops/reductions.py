# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0

from enum import Enum
from typing import Literal, Tuple

import torch
from jaxtyping import Float, Int
from torch import Tensor
from torch_scatter import segment_csr


class REDUCTIONS(Enum):
    MIN = "min"
    MAX = "max"
    MEAN = "mean"
    SUM = "sum"
    MUL = "mul"
    VAR = "var"
    STD = "std"
    RANDOM = "random"


REDUCTION_TYPES_STR = Literal["min", "max", "mean", "sum", "mul", "var", "std", "random"]


def _var(
    features: Float[Tensor, "N F"],
    neighbor_row_splits: Int[Tensor, "M"],  # noqa
) -> Tuple[Float[Tensor, "M F"], Float[Tensor, "M F"]]:  # noqa
    out_mean = segment_csr(features, neighbor_row_splits, reduce="mean")
    out_var = segment_csr(features**2, neighbor_row_splits, reduce="mean") - out_mean**2
    return out_var, out_mean


def row_reduction(
    features: Float[Tensor, "N F"],  # noqa
    neighbor_row_splits: Int[Tensor, "M+1"],  # noqa
    reduction: REDUCTIONS,
    eps: float = 1e-6,
) -> Float[Tensor, "M F"]:  # noqa
    if isinstance(reduction, str):
        reduction = REDUCTIONS(reduction)

    assert (
        len(features) == neighbor_row_splits[-1].item()
    ), f"Features length {len(features)} must match the last row split {neighbor_row_splits[-1].item()}"

    if reduction in [
        REDUCTIONS.MIN,
        REDUCTIONS.MAX,
        REDUCTIONS.MEAN,
        REDUCTIONS.SUM,
        REDUCTIONS.MUL,
    ]:
        out_feature = segment_csr(features, neighbor_row_splits, reduce=str(reduction.value))
    elif reduction == REDUCTIONS.VAR:
        out_feature = _var(features, neighbor_row_splits)[0]
    elif reduction == REDUCTIONS.STD:
        out_feature = torch.sqrt(_var(features, neighbor_row_splits)[0] + eps)
    elif reduction == REDUCTIONS.RANDOM:
        num_per_row = neighbor_row_splits.diff()
        rand_idx = (
            (torch.rand(len(num_per_row), device=num_per_row.device) * num_per_row).floor().long()
        )
        sample_idx = rand_idx + neighbor_row_splits[:-1]
        out_feature = features[sample_idx.to(features.device)]
    else:
        raise ValueError(f"Invalid reduction: {reduction}")
    return out_feature
