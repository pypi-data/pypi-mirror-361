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

import random
from typing import Optional, Tuple, Union

import cupy as cp
import torch
import torch.nn as nn
from jaxtyping import Int
from torch import Tensor
from warpconvnet.geometry.coords.ops.serialization import (
    POINT_ORDERING,
    SerializationResult,
    encode,
)
from warpconvnet.utils.ravel import ravel_multi_index_auto_shape
from warpconvnet.utils.unique import unique_segmented

_COORD_TO_CODE_CUDA = """
typedef signed int int32_t;
typedef long long int64_t;

__device__ int64_t part1by2_long(int64_t n) {
    n &= 0x1fffff;                    // mask to 21 bits
    n = (n | (n << 32)) & 0x1f00000000ffff;
    n = (n | (n << 16)) & 0x1f0000ff0000ff;
    n = (n | (n << 8))  & 0x100f00f00f00f00f;
    n = (n | (n << 4))  & 0x10c30c30c30c30c3;
    n = (n | (n << 2))  & 0x1249249249249249;
    return n;
}

// Morton code for 20-bit coordinates
__device__ int64_t morton_code_20bit_device(int64_t coord_x, int64_t coord_y, int64_t coord_z) {
    // Calculate the Morton order for 3 coordinates (max 21 bits each for 63-bit total)
    return (part1by2_long(coord_z) << 2) | (part1by2_long(coord_y) << 1) | part1by2_long(coord_x);
}

// Add the (grid_coord + coord_offset - min_coord) // window_size to generate morton code
extern "C" __global__ void coord_to_code_kernel(
    const int* grid_coord,
    const int* coord_offset,
    const int* min_coord,
    const int* window_size,
    const int N,
    int64_t* codes
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= N) return;

    // Load offset, min, and window_size into shared memory
    __shared__ int s_coord_offset[3];
    __shared__ int s_min_coord[3];
    __shared__ int s_window_size[3];
    if (threadIdx.x < 3) {
        s_coord_offset[threadIdx.x] = coord_offset[threadIdx.x];
        s_min_coord[threadIdx.x] = min_coord[threadIdx.x];
        s_window_size[threadIdx.x] = window_size[threadIdx.x];
    }
    __syncthreads();

    // Load grid coordinates
    int grid_coord_x = grid_coord[idx * 3 + 0];
    int grid_coord_y = grid_coord[idx * 3 + 1];
    int grid_coord_z = grid_coord[idx * 3 + 2];

    // Compute voxel coordinates: (grid_coord + coord_offset - min_coord) / window_size
    int64_t voxel_x = (grid_coord_x + s_coord_offset[0] - s_min_coord[0]) / s_window_size[0];
    int64_t voxel_y = (grid_coord_y + s_coord_offset[1] - s_min_coord[1]) / s_window_size[1];
    int64_t voxel_z = (grid_coord_z + s_coord_offset[2] - s_min_coord[2]) / s_window_size[2];

    // Compute morton code
    int64_t code = morton_code_20bit_device(voxel_x, voxel_y, voxel_z);
    codes[idx] = code;
}
"""


STR2COORD_OFFSET = {
    "random": (None, None, None),
    "zero": (0, 0, 0),
    "x": (0.5, 0, 0),
    "y": (0, 0.5, 0),
    "z": (0, 0, 0.5),
    "xy": (0.5, 0.5, 0),
    "xz": (0.5, 0, 0.5),
    "yz": (0, 0.5, 0.5),
    "xyz": (0.5, 0.5, 0.5),
}


# Encode using voxel size
@torch.no_grad()
def voxel_encode(
    grid_coord: Int[Tensor, "N 3"],
    batch_offsets: Optional[Int[Tensor, "B+1"]] = None,
    window_size: Optional[Union[int, Tuple[int, int, int]]] = None,
    coord_offset: Union[str, Tuple[float, float, float]] = (0.0, 0.0, 0.0),
    return_perm: bool = False,
    return_inverse: bool = False,
    return_counts: bool = False,
    encoding_method: str = "ravel",
) -> Union[Int[Tensor, "N"], SerializationResult]:  # noqa: F821
    """
    encode voxel coordinates that fall within a window as the same code.

    Args:
        grid_coord: Grid coordinates (N, 3)
        batch_offsets: Batch offsets for multi-batch processing.
        coord_offset: Coordinate offset for voxel encoding.
        window_size: Window size for voxel encoding. Can be a single integer (applied to all dimensions)
                    or a tuple of three integers for per-dimension window sizes (x, y, z).
        return_perm: Whether to return the permutation that sorts the coordinates by their codes.
        return_inverse: Whether to return the inverse permutation.
        encoding_method: Method to use for encoding ('morton' for Morton code, 'ravel' for ravel_multi_index)

    """
    # Handle empty coordinates
    if grid_coord.shape[0] == 0:
        codes = torch.empty(0, dtype=torch.int64, device=grid_coord.device)
        if not return_perm and not return_inverse:
            return codes
        return SerializationResult(
            codes=codes,
            perm=(
                torch.empty(0, dtype=torch.int64, device=grid_coord.device)
                if return_perm
                else None
            ),
            inverse_perm=(
                torch.empty(0, dtype=torch.int64, device=grid_coord.device)
                if return_inverse
                else None
            ),
            counts=(
                torch.empty(0, dtype=torch.int64, device=grid_coord.device)
                if return_counts
                else None
            ),
        )

    assert grid_coord.shape[1] == 3, "grid_coord must be a 3D tensor"
    assert encoding_method in [
        "morton",
        "ravel",
    ], f"encoding_method must be 'morton' or 'ravel', got {encoding_method}"

    # Handle coordinate offset
    if isinstance(coord_offset, str):
        if coord_offset == "random":
            coord_offset = (random.random(), random.random(), random.random())
        else:
            coord_offset = STR2COORD_OFFSET[coord_offset]

    assert (
        isinstance(coord_offset, tuple) and len(coord_offset) == 3
    ), "coord_offset must be a tuple of 3 floats"

    # Handle window_size - convert to tuple if single integer
    assert window_size is not None, "window_size must be provided"
    if isinstance(window_size, int):
        window_size = (window_size, window_size, window_size)

    assert (
        isinstance(window_size, tuple) and len(window_size) == 3
    ), "window_size must be an integer or a tuple of 3 integers"

    # Convert window_size to tensor
    window_size_tensor = torch.tensor(window_size, dtype=torch.int32)

    # Convert coord_offset to tensor and round to nearest integer
    coord_offset_tensor = (
        torch.round(torch.tensor(coord_offset, dtype=torch.float32) * window_size_tensor.float())
        .int()
        .to(grid_coord.device)
    )

    min_coord = grid_coord.min(dim=0).values.int()

    if encoding_method == "morton":
        # Original Morton code implementation
        # Prepare data for CUDA kernel
        N = grid_coord.shape[0]
        grid_coord_int = grid_coord.int().contiguous()

        # Compile CUDA kernel
        module = cp.RawModule(code=_COORD_TO_CODE_CUDA)
        kernel = module.get_function("coord_to_code_kernel")

        # Prepare CuPy arrays
        grid_coord_cp = cp.asarray(grid_coord_int)
        coord_offset_cp = cp.asarray(coord_offset_tensor)
        min_coord_cp = cp.asarray(min_coord)
        window_size_cp = cp.asarray(window_size_tensor)
        codes_cp = cp.empty(N, dtype=cp.int64)

        # Launch kernel
        threads_per_block = 256
        blocks_per_grid = (N + threads_per_block - 1) // threads_per_block

        kernel(
            (blocks_per_grid,),
            (threads_per_block,),
            (grid_coord_cp, coord_offset_cp, min_coord_cp, window_size_cp, N, codes_cp),
        )
        torch.cuda.current_stream().synchronize()

        # Convert back to PyTorch tensor
        codes = torch.as_tensor(codes_cp, device=grid_coord.device)

    else:  # encoding_method == "ravel"
        # Use ravel_multi_index for encoding

        # Calculate voxel coordinates: (grid_coord + coord_offset - min_coord) / window_size
        voxel_coord = (grid_coord + coord_offset_tensor - min_coord) // window_size_tensor.to(
            grid_coord.device
        )

        # Compute codes using ravel_multi_index with auto shape
        codes = ravel_multi_index_auto_shape(voxel_coord, dim=0)

    # Return codes only if no permutations requested
    if not return_perm and not return_inverse and not return_counts:
        return codes

    counts = None
    # Generate permutation if requested
    if batch_offsets is not None:
        # Use segmented sort for batched data
        import warpconvnet._C as _C

        perm, sorted_codes = _C.utils.segmented_sort(
            codes,
            batch_offsets.to(codes.device),
            descending=False,
            return_indices=True,
        )
        unique_codes, counts = unique_segmented(
            sorted_codes, batch_offsets.cpu(), return_counts=return_counts
        )
    else:
        perm = torch.argsort(codes)
        if return_counts:
            counts = torch.unique_consecutive(codes, return_counts=True)[1]

    # Generate inverse permutation if requested
    inverse_perm = None
    if return_inverse:
        inverse_perm = torch.zeros_like(perm).scatter_(
            0, perm, torch.arange(len(perm), device=perm.device)
        )

    return SerializationResult(
        codes=codes,
        perm=perm if return_perm else None,
        inverse_perm=inverse_perm,
        counts=counts,
    )


if __name__ == "__main__":
    B = 3
    N_min, N_max = 5, 10
    torch.manual_seed(0)
    Ns = [random.randint(N_min, N_max) for _ in range(B)]
    grid_coord = torch.randint(0, 10, (sum(Ns), 3)).cuda()
    batch_offsets = torch.cat([torch.zeros(1), torch.cumsum(torch.tensor(Ns), dim=0)]).int()
    print(f"Batch offsets: {batch_offsets}")
    print(f"Grid coord: {grid_coord}")

    # Test Morton encoding
    print("\n--- Morton Encoding ---")
    result = voxel_encode(
        grid_coord,
        batch_offsets,
        window_size=5,
        return_perm=True,
        return_counts=True,
        encoding_method="morton",
    )
    if isinstance(result, SerializationResult):
        print(f"Codes: {result.codes}")
        print(f"Permuted codes: {result.codes[result.perm]}")
        print(f"Perm: {result.perm}")
        print(f"Counts: {result.counts}")

    # Test Ravel encoding
    print("\n--- Ravel Encoding ---")
    result_ravel = voxel_encode(
        grid_coord,
        batch_offsets,
        window_size=5,
        return_perm=True,
        return_counts=True,
        encoding_method="ravel",
    )
    if isinstance(result_ravel, SerializationResult):
        print(f"Codes: {result_ravel.codes}")
        print(f"Permuted codes: {result_ravel.codes[result_ravel.perm]}")
        print(f"Perm: {result_ravel.perm}")
        print(f"Counts: {result_ravel.counts}")
