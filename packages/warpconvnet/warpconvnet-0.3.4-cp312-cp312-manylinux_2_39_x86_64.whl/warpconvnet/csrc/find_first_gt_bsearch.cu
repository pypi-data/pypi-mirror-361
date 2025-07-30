// SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

// Common device function for binary search to find the first element > key
__device__ int bsearch_first_gt(int key, const int *smem, int M) {
  int left = 0, right = M;  // search in [0, M)
  while (left < right) {    // binary search loop
    int mid = (left + right) >> 1;
    if (key < smem[mid]) {
      right = mid;  // first greater must be left of or at mid
    } else {
      left = mid + 1;  // skip mid, search right half
    }
  }
  // left == first index where smem[left] > key, or left==M if none
  return (left < M) ? left : -1;
}

extern "C" __global__ void find_first_gt_bsearch(const int *__restrict__ srcM,
                                                 int M,
                                                 const int *__restrict__ srcN,
                                                 int N,
                                                 int *__restrict__ out) {
  extern __shared__ int smem[];  // dynamic shared memory
  int tid = threadIdx.x;

  // Load sorted M elements into shared memory
  for (int i = tid; i < M; i += blockDim.x) {
    smem[i] = srcM[i];
  }
  __syncthreads();  // ensure smem[] is ready

  // Compute global thread index over N
  int idx = blockIdx.x * blockDim.x + tid;
  if (idx < N) {
    int key = srcN[idx];
    out[idx] = bsearch_first_gt(key, smem, M) - 1;
  }
}

// Find the first index where the arange index is greater than the sorted array M
extern "C" __global__ void find_first_gt_bsearch_arange(const int *__restrict__ srcM,
                                                        int M,
                                                        int N,
                                                        int *__restrict__ out) {
  extern __shared__ int smem[];  // dynamic shared memory
  int tid = threadIdx.x;

  // Load sorted M elements into shared memory
  for (int i = tid; i < M; i += blockDim.x) {
    smem[i] = srcM[i];
  }
  __syncthreads();  // ensure smem[] is ready

  // Compute global thread index over N
  int idx = blockIdx.x * blockDim.x + tid;
  if (idx < N) {
    int key = idx;
    out[idx] = bsearch_first_gt(key, smem, M) - 1;
  }
}
