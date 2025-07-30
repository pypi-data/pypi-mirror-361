// SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
// SPDX-License-Identifier: Apache-2.0

typedef unsigned int uint32_t;

// --- Hash Helper Functions ---

__device__ inline uint32_t murmur_32_scramble(uint32_t k) {
  k *= 0xCC9E2D51;
  k = (k << 15) | (k >> 17);
  k *= 0x1B873593;
  return k;
}

__device__ inline uint32_t _hash_murmur_impl(uint32_t h, uint32_t k) {
  h ^= murmur_32_scramble(k);
  h = (h << 13) | (h >> 19);
  h = h * 5 + 0xE6546B64;
  return h;
}

__device__ inline uint32_t _hash_murmur_finalize(uint32_t h, int length_bytes) {
  h ^= length_bytes;
  h ^= h >> 16;
  h *= 0x85EBCA6B;
  h ^= h >> 13;
  h *= 0xC2B2AE35;
  h ^= h >> 16;
  return h;
}

__device__ inline uint32_t _hash_fnv1a_impl(uint32_t hash_val, uint32_t key) {
  hash_val ^= key;
  hash_val *= 16777619;  // FNV prime
  return hash_val;
}

__device__ inline uint32_t _hash_city_impl(uint32_t hash_val, uint32_t key) {
  hash_val += key * 0x9E3779B9;
  hash_val ^= hash_val >> 16;
  hash_val *= 0x85EBCA6B;
  hash_val ^= hash_val >> 13;
  hash_val *= 0xC2B2AE35;
  hash_val ^= hash_val >> 16;
  return hash_val;
}

// --- Array Hash Functions ---

// key: pointer to the start of the integer array key
// key_dim: number of integers in the key
// capacity: size of the hash table
__device__ inline int hash_fnv1a_array(const int* key, int key_dim, int capacity) {
  uint32_t hash_val = 2166136261u;  // FNV offset basis
  for (int i = 0; i < key_dim; ++i) {
    hash_val = _hash_fnv1a_impl(hash_val, (uint32_t)key[i]);
  }
  // Use signed modulo to match Warp's behavior potentially
  int signed_hash = (int)hash_val;
  return ((signed_hash % capacity) + capacity) % capacity;
}

__device__ inline int hash_city_array(const int* key, int key_dim, int capacity) {
  uint32_t hash_val = 0;
  for (int i = 0; i < key_dim; ++i) {
    hash_val = _hash_city_impl(hash_val, (uint32_t)key[i]);
  }
  int signed_hash = (int)hash_val;
  return ((signed_hash % capacity) + capacity) % capacity;
}

__device__ inline int hash_murmur_array(const int* key, int key_dim, int capacity) {
  uint32_t h = 0x9747B28Cu;  // Seed
  for (int i = 0; i < key_dim; ++i) {
    h = _hash_murmur_impl(h, (uint32_t)key[i]);
  }
  // Finalize (assuming key_dim * 4 bytes)
  h = _hash_murmur_finalize(h, key_dim * 4);
  int signed_hash = (int)h;
  return ((signed_hash % capacity) + capacity) % capacity;
}

// --- Hash Function Structs/Functors ---

struct FNV1AHash {
  __device__ inline static int hash(const int* key, int key_dim, int capacity) {
    uint32_t hash_val = 2166136261u;  // FNV offset basis
    for (int i = 0; i < key_dim; ++i) {
      hash_val = _hash_fnv1a_impl(hash_val, (uint32_t)key[i]);
    }
    int signed_hash = (int)hash_val;
    return ((signed_hash % capacity) + capacity) % capacity;
  }
};

struct CityHash {
  __device__ inline static int hash(const int* key, int key_dim, int capacity) {
    uint32_t hash_val = 0;
    for (int i = 0; i < key_dim; ++i) {
      hash_val = _hash_city_impl(hash_val, (uint32_t)key[i]);
    }
    int signed_hash = (int)hash_val;
    return ((signed_hash % capacity) + capacity) % capacity;
  }
};

struct MurmurHash {
  __device__ inline static int hash(const int* key, int key_dim, int capacity) {
    uint32_t h = 0x9747B28Cu;  // Seed
    for (int i = 0; i < key_dim; ++i) {
      h = _hash_murmur_impl(h, (uint32_t)key[i]);
    }
    // Finalize (assuming key_dim * 4 bytes)
    h = _hash_murmur_finalize(h, key_dim * 4);
    int signed_hash = (int)h;
    return ((signed_hash % capacity) + capacity) % capacity;
  }
};

// --- Vector Comparison ---
// a, b: pointers to the start of the vectors
// dim: dimension of the vectors
__device__ inline bool vec_equal(const int* a, const int* b, int dim) {
  for (int i = 0; i < dim; ++i) {
    if (a[i] != b[i]) {
      return false;
    }
  }
  return true;
}

// --- Device Function for Hash Table Search ---
template <typename HashFuncT>
__device__ inline int search_hash_table(
    const int* __restrict__ table_kvs,    // Pointer to key-value store
    const int* __restrict__ vector_keys,  // Pointer to original vector keys
    const int* __restrict__ query_key,    // Pointer to the key being searched
    int key_dim,                          // Dimension of keys
    int table_capacity) {                 // Capacity of the hash table

  // Use the templated hash function directly
  int slot = HashFuncT::hash(query_key, key_dim, table_capacity);
  int initial_slot = slot;
  int attempts = 0;

  while (attempts < table_capacity) {
    // Read the slot marker first. If it's -1, the slot is truly empty.
    int slot_marker = table_kvs[slot * 2 + 0];

    if (slot_marker == -1) {
      // Found an empty slot in the probe sequence, key is not present.
      return -1;
    }

    // Slot is potentially occupied. Read the index stored in the value part.
    int vector_index = table_kvs[slot * 2 + 1];

    // Check for invalid index (e.g., if insertion failed or slot marker is stale)
    if (vector_index != -1) {
      const int* candidate_key = &vector_keys[vector_index * key_dim];
      if (vec_equal(candidate_key, query_key, key_dim)) {
        // Keys match!
        return vector_index;
      }
    }
    // If keys don't match or index was invalid, continue probing.
    slot = (slot + 1) % table_capacity;

    if (slot == initial_slot) {
      // Cycled through all slots without finding the key or an empty slot.
      return -1;
    }
    attempts++;
  }
  // Exceeded attempts (should indicate an issue or extremely full table).
  return -1;
}

// --- Kernels ---

// Kernel to initialize the hash table slots to -1
extern "C" __global__ void prepare_key_value_pairs_kernel(int* table_kvs, int capacity) {
  int tid = blockIdx.x * blockDim.x + threadIdx.x;
  if (tid < capacity) {
    table_kvs[2 * tid + 0] = -1;  // Key hash slot indicator
    table_kvs[2 * tid + 1] = -1;  // Value (index into vector_keys)
  }
}

// --- Templated Insert Kernel ---
template <typename HashFuncT>
__global__ void insert_kernel_templated(
    int* table_kvs, const int* vector_keys, int num_keys, int key_dim, int table_capacity) {
  int idx = blockIdx.x * blockDim.x + threadIdx.x;
  if (idx >= num_keys) {
    return;
  }

  const int* key_to_insert = &vector_keys[idx * key_dim];
  // Use the templated hash function directly
  int slot = HashFuncT::hash(key_to_insert, key_dim, table_capacity);
  int initial_slot = slot;
  int attempts = 0;

  while (attempts < table_capacity) {
    int* slot_address = &table_kvs[slot * 2];
    // Store the *original index* (idx) in the compare field, not the slot.
    // This prevents overwriting if two different keys hash to the same slot initially.
    // We are essentially using the first element of the pair to *reserve* the slot
    // via atomicCAS, and the second to store the value (original index).
    // We store the actual index idx+1 temporarily to distinguish from initial -1.
    // Let's refine this: Store 'slot' in compare field as originally, seems simpler.
    int prev = atomicCAS(slot_address, -1, slot);  // Try to claim the slot marker

    if (prev == -1) {
      // Slot claimed successfully, now store the actual value index
      table_kvs[slot * 2 + 1] = idx;
      // Optional: store the actual hash value in table_kvs[slot*2 + 0] = slot;
      // Already done by atomicCAS if successful.
      return;
    }

    // Collision or slot already claimed
    slot = (slot + 1) % table_capacity;

    if (slot == initial_slot) {
      // Table is full or couldn't find an empty slot after full circle
      // Consider adding a mechanism to signal failure if needed.
      return;
    }
    attempts++;
  }
  // Exceeded attempts (should only happen if table is pathologically full)
}

// --- Templated Search Kernel ---
template <typename HashFuncT>
__global__ void search_kernel_templated(const int* __restrict__ table_kvs,
                                        const int* __restrict__ vector_keys,
                                        const int* __restrict__ search_keys,
                                        int* __restrict__ results,
                                        int num_search_keys,
                                        int key_dim,
                                        int table_capacity) {
  int idx = blockIdx.x * blockDim.x + threadIdx.x;
  if (idx >= num_search_keys) {
    return;
  }

  const int* query_key = &search_keys[idx * key_dim];
  results[idx] =
      search_hash_table<HashFuncT>(table_kvs, vector_keys, query_key, key_dim, table_capacity);
}

// --- Extern "C" Wrappers for CuPy ---

// Insert Wrappers
extern "C" __global__ void insert_kernel_fnv1a(
    int* table_kvs, const int* vector_keys, int num_keys, int key_dim, int table_capacity) {
  insert_kernel_templated<FNV1AHash>(table_kvs, vector_keys, num_keys, key_dim, table_capacity);
}
extern "C" __global__ void insert_kernel_city(
    int* table_kvs, const int* vector_keys, int num_keys, int key_dim, int table_capacity) {
  insert_kernel_templated<CityHash>(table_kvs, vector_keys, num_keys, key_dim, table_capacity);
}
extern "C" __global__ void insert_kernel_murmur(
    int* table_kvs, const int* vector_keys, int num_keys, int key_dim, int table_capacity) {
  insert_kernel_templated<MurmurHash>(table_kvs, vector_keys, num_keys, key_dim, table_capacity);
}

// Search Wrappers
extern "C" __global__ void search_kernel_fnv1a(const int* table_kvs,
                                               const int* vector_keys,
                                               const int* search_keys,
                                               int* results,
                                               int num_search_keys,
                                               int key_dim,
                                               int table_capacity) {
  search_kernel_templated<FNV1AHash>(
      table_kvs, vector_keys, search_keys, results, num_search_keys, key_dim, table_capacity);
}
extern "C" __global__ void search_kernel_city(const int* table_kvs,
                                              const int* vector_keys,
                                              const int* search_keys,
                                              int* results,
                                              int num_search_keys,
                                              int key_dim,
                                              int table_capacity) {
  search_kernel_templated<CityHash>(
      table_kvs, vector_keys, search_keys, results, num_search_keys, key_dim, table_capacity);
}
extern "C" __global__ void search_kernel_murmur(const int* table_kvs,
                                                const int* vector_keys,
                                                const int* search_keys,
                                                int* results,
                                                int num_search_keys,
                                                int key_dim,
                                                int table_capacity) {
  search_kernel_templated<MurmurHash>(
      table_kvs, vector_keys, search_keys, results, num_search_keys, key_dim, table_capacity);
}
