# Benchmark

Here is an explanation of the benchmark comparison in this folder:

This directory contains scripts to compare the performance of two Python routing libraries: **autoroutes** and the Python binding of **matchit** (via `pymatchit`). The benchmarks are performed as follows:

1. **Adding 10,000 routes** to each router implementation.
2. Performing route matching in several scenarios:
    - Matching the first route (`/inc/0`)
    - Matching a middle route (`/inc/5000`)
    - Matching a non-existent route (`/notfound`)
3. Measuring the execution time of route matching using the `timeit` module, and profiling performance with `cProfile`.

The relevant files are:

- `bench_autoroutes.py` and `profile_autoroutes.py` for benchmarking and profiling autoroutes.
- `bench_pymatchit.py` and `profile_pymatchit.py` for benchmarking and profiling pymatchit.

The goal of this comparison is to evaluate how fast and efficient each library is at handling a large number of routes, and to observe the performance overhead in different matching scenarios (first, middle, and not found).

The benchmark results can help determine which library is more suitable for applications that require high performance and need to manage a large number of routes.

## 🚀 Latest Routing Benchmark: `pymatchit` 🆚 `autoroutes` (10,000 routes)

| ⚙️ Operation               | 🐍 `pymatchit` (ms) | 🐢 `autoroutes` (ms) | 📌 Notes                                            |
| ------------------------- | ------------------ | ------------------- | -------------------------------------------------- |
| 📦 Load 10,000 Routes      | ⚡ **24.815**       | 🐢 9,066.554         | `pymatchit` is **~365× faster** at loading.        |
| 🔎 Find `/inc/0`           | ⚡ **25.674**       | 27.865              | `pymatchit` is slightly faster.                    |
| 🔎 Find `/inc/1000`        | ⚡ **37.006**       | 57.326              | `pymatchit` is ~1.55× faster.                      |
| 🔎 Find `/inc/1500`        | ⚡ **31.453**       | 64.458              | `pymatchit` is ~2× faster.                         |
| 🔎 Find `/inc/3000`        | ⚡ **29.429**       | 60.624              | `pymatchit` is ~2× faster.                         |
| 🔀 Middle path `/inc/5000` | ⚡ **31.826**       | 64.408              | `pymatchit` is ~2× faster.                         |
| ❓ Unknown path            | 19.993             | ⚡ **19.177**        | `autoroutes` slightly faster when path is missing. |

### 📊 Quick Summary

- 🥇 `pymatchit` **wins almost everywhere**, especially in load time and valid path lookup.
- 🥈 `autoroutes` is **only slightly better** when path is missing.
- ✅ For large routing tables and fast lookup, **`pymatchit` remains the optimal choice**.
