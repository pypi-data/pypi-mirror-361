// SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

typedef signed int int32_t;
typedef long long int64_t;
typedef unsigned int uint32_t;
typedef unsigned long long uint64_t;

// Helper function for 3D space-out bit (from hash_fns.cuh)
__device__ __forceinline__ uint64_t space_out_bit_3d(uint64_t x) {
  x = (x | x << 32) & 0x1f00000000ffff;
  x = (x | x << 16) & 0x1f0000ff0000ff;
  x = (x | x << 8) & 0x100f00f00f00f00f;
  x = (x | x << 4) & 0x10c30c30c30c30c3;
  x = (x | x << 2) & 0x1249249249249249;
  return x;
}

// Hash function types enum
enum HashType {
  XORSUM_DIV = 0,
  XORSUM_MOD = 1,
  ZORDER_DIV = 2,
  ZORDER_MOD = 3,
  SUM_DIV = 4
};

// Templated hash function
template<HashType hash_type>
__device__ __forceinline__ int64_t compute_hash(int coord_x, int coord_y, int coord_z, int64_t param) {
  if constexpr (hash_type == XORSUM_DIV) {
    int64_t acc = (int64_t)coord_x ^ (int64_t)coord_y ^ (int64_t)coord_z;
    return acc / param;
  } else if constexpr (hash_type == XORSUM_MOD) {
    int64_t acc = (int64_t)coord_x ^ (int64_t)coord_y ^ (int64_t)coord_z;
    return acc % param;
  } else if constexpr (hash_type == ZORDER_DIV) {
    uint64_t x = space_out_bit_3d((uint64_t)coord_x);
    uint64_t y = space_out_bit_3d((uint64_t)coord_y);
    uint64_t z = space_out_bit_3d((uint64_t)coord_z);
    int64_t interleaved = (x | y << 1 | z << 2) >> 31;
    return interleaved / param;
  } else if constexpr (hash_type == ZORDER_MOD) {
    uint64_t x = space_out_bit_3d((uint64_t)coord_x);
    uint64_t y = space_out_bit_3d((uint64_t)coord_y);
    uint64_t z = space_out_bit_3d((uint64_t)coord_z);
    int64_t interleaved = (x | y << 1 | z << 2) >> 31;
    return interleaved % param;
  } else if constexpr (hash_type == SUM_DIV) {
    int64_t acc = (int64_t)coord_x + (int64_t)coord_y + (int64_t)coord_z;
    return acc / param;
  }
  return 0; // Should never reach here
}



// Explicit template instantiations for C linkage - Single batch kernels
extern "C" __global__ void xorsum_div_kernel(
    const int* __restrict__ coords_data,
    int num_points,
    int64_t param,
    int64_t* __restrict__ result_codes) {
  int tid = blockIdx.x * blockDim.x + threadIdx.x;
  if (tid < num_points) {
    int coord_x = coords_data[tid * 3 + 0];
    int coord_y = coords_data[tid * 3 + 1];
    int coord_z = coords_data[tid * 3 + 2];
    result_codes[tid] = compute_hash<XORSUM_DIV>(coord_x, coord_y, coord_z, param);
  }
}

extern "C" __global__ void xorsum_mod_kernel(
    const int* __restrict__ coords_data,
    int num_points,
    int64_t param,
    int64_t* __restrict__ result_codes) {
  int tid = blockIdx.x * blockDim.x + threadIdx.x;
  if (tid < num_points) {
    int coord_x = coords_data[tid * 3 + 0];
    int coord_y = coords_data[tid * 3 + 1];
    int coord_z = coords_data[tid * 3 + 2];
    result_codes[tid] = compute_hash<XORSUM_MOD>(coord_x, coord_y, coord_z, param);
  }
}

extern "C" __global__ void zorder_div_kernel(
    const int* __restrict__ coords_data,
    int num_points,
    int64_t param,
    int64_t* __restrict__ result_codes) {
  int tid = blockIdx.x * blockDim.x + threadIdx.x;
  if (tid < num_points) {
    int coord_x = coords_data[tid * 3 + 0];
    int coord_y = coords_data[tid * 3 + 1];
    int coord_z = coords_data[tid * 3 + 2];
    result_codes[tid] = compute_hash<ZORDER_DIV>(coord_x, coord_y, coord_z, param);
  }
}

extern "C" __global__ void zorder_mod_kernel(
    const int* __restrict__ coords_data,
    int num_points,
    int64_t param,
    int64_t* __restrict__ result_codes) {
  int tid = blockIdx.x * blockDim.x + threadIdx.x;
  if (tid < num_points) {
    int coord_x = coords_data[tid * 3 + 0];
    int coord_y = coords_data[tid * 3 + 1];
    int coord_z = coords_data[tid * 3 + 2];
    result_codes[tid] = compute_hash<ZORDER_MOD>(coord_x, coord_y, coord_z, param);
  }
}

extern "C" __global__ void sum_div_kernel(
    const int* __restrict__ coords_data,
    int num_points,
    int64_t param,
    int64_t* __restrict__ result_codes) {
  int tid = blockIdx.x * blockDim.x + threadIdx.x;
  if (tid < num_points) {
    int coord_x = coords_data[tid * 3 + 0];
    int coord_y = coords_data[tid * 3 + 1];
    int coord_z = coords_data[tid * 3 + 2];
    result_codes[tid] = compute_hash<SUM_DIV>(coord_x, coord_y, coord_z, param);
  }
}

// Explicit template instantiations for C linkage - Batched kernels
extern "C" __global__ void xorsum_div_batched_kernel(
    const int* __restrict__ bcoords_data,
    int num_points,
    int64_t param,
    int64_t* __restrict__ result_codes) {
  int tid = blockIdx.x * blockDim.x + threadIdx.x;
  if (tid < num_points) {
    int coord_x = bcoords_data[tid * 4 + 1];
    int coord_y = bcoords_data[tid * 4 + 2];
    int coord_z = bcoords_data[tid * 4 + 3];
    result_codes[tid] = compute_hash<XORSUM_DIV>(coord_x, coord_y, coord_z, param);
  }
}

extern "C" __global__ void xorsum_mod_batched_kernel(
    const int* __restrict__ bcoords_data,
    int num_points,
    int64_t param,
    int64_t* __restrict__ result_codes) {
  int tid = blockIdx.x * blockDim.x + threadIdx.x;
  if (tid < num_points) {
    int coord_x = bcoords_data[tid * 4 + 1];
    int coord_y = bcoords_data[tid * 4 + 2];
    int coord_z = bcoords_data[tid * 4 + 3];
    result_codes[tid] = compute_hash<XORSUM_MOD>(coord_x, coord_y, coord_z, param);
  }
}

extern "C" __global__ void zorder_div_batched_kernel(
    const int* __restrict__ bcoords_data,
    int num_points,
    int64_t param,
    int64_t* __restrict__ result_codes) {
  int tid = blockIdx.x * blockDim.x + threadIdx.x;
  if (tid < num_points) {
    int coord_x = bcoords_data[tid * 4 + 1];
    int coord_y = bcoords_data[tid * 4 + 2];
    int coord_z = bcoords_data[tid * 4 + 3];
    result_codes[tid] = compute_hash<ZORDER_DIV>(coord_x, coord_y, coord_z, param);
  }
}

extern "C" __global__ void zorder_mod_batched_kernel(
    const int* __restrict__ bcoords_data,
    int num_points,
    int64_t param,
    int64_t* __restrict__ result_codes) {
  int tid = blockIdx.x * blockDim.x + threadIdx.x;
  if (tid < num_points) {
    int coord_x = bcoords_data[tid * 4 + 1];
    int coord_y = bcoords_data[tid * 4 + 2];
    int coord_z = bcoords_data[tid * 4 + 3];
    result_codes[tid] = compute_hash<ZORDER_MOD>(coord_x, coord_y, coord_z, param);
  }
}

extern "C" __global__ void sum_div_batched_kernel(
    const int* __restrict__ bcoords_data,
    int num_points,
    int64_t param,
    int64_t* __restrict__ result_codes) {
  int tid = blockIdx.x * blockDim.x + threadIdx.x;
  if (tid < num_points) {
    int coord_x = bcoords_data[tid * 4 + 1];
    int coord_y = bcoords_data[tid * 4 + 2];
    int coord_z = bcoords_data[tid * 4 + 3];
    result_codes[tid] = compute_hash<SUM_DIV>(coord_x, coord_y, coord_z, param);
  }
} 