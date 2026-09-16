# Project Brahmaand 🌌
### Sovereign, Non-Autoregressive Edge Intelligence via 24-Dimensional Topological Cartridges, Zero-Multiplication Subtractive Meshes, and Predictive B-Frames

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22800741.svg)](https://doi.org/10.5281/zenodo.22800741)
[![License: BSL 1.1](https://img.shields.io/badge/License-BSL%201.1%20(Free%20Research%20%2F%20Commercial%20Paid)-orange.svg)](LICENSE)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-black?logo=vercel)](https://bananamilk.vercel.app)
[![Inference Cost](https://img.shields.io/badge/Cloud%20Inference%20Cost-%240.00-success)](#)

---

## 📖 Overview

**Project Brahmaand** is a sovereign, offline-first neuro-symbolic intelligence architecture designed to run on ultra-low-power edge silicon ($50 smartphones, embedded microcontrollers, and offline edge nodes) at **$0.00 cloud inference cost**.

Instead of relying on multi-billion parameter autoregressive transformer decoders that require floating-point Multiply-Accumulate (MAC) hardware, Brahmaand introduces:
1. **24-Dimensional Continuous Topological Manifolds** with Grassmannian chordal projection.
2. **Zero-Multiplication Subtractive Meshes** powered exclusively by Power-of-Two (PO2) bitshifts and additions.
3. **Domain-Specific Binary Cartridges (.otmb)** with zero-copy mmap cold starts (<1.2 ms).
4. **Parth Edge Agent**: A decoupled dual-mode speaker with hardware-isolated **Deterministic Truth Engine** and **Predictive B-Frame Solver**.

---

## 📂 Repository Structure

```text
brahmaand/
├── paper/                      # Academic preprint & LaTeX sources
│   ├── project_brahmand.pdf    # Full compiled 6-page research paper
│   └── brahmand_paper.tex      # Complete LaTeX source
├── cpp_core/                   # High-performance C++ header-only engine
│   └── otm_engine.hpp          # Zero-multiplication bitshift manifold kernel
├── python_mesh/                # Reference Python implementations & benchmarks
│   ├── otm_mesh.py             # Subtractive mesh & topological operations
│   ├── node_proportional_otm.py# Node-proportional scaling & routing
│   ├── bitwise_kernel.py       # Pure bitwise arithmetic transforms
│   ├── benchmark.py            # Latency, throughput & FLOPS benchmark suite
│   └── run_full_suite.py       # Full empirical test harness
├── web_harness/                # Interactive PWA research prototype
│   ├── index.html              # Glass-box visualization & Parth agent UI
│   ├── cartridges.json         # Master domain cartridge data
│   ├── manifest.json           # Offline PWA manifest
│   └── sw.js                   # Service Worker for 100% offline edge caching
├── cartridges/                 # Pre-compiled knowledge cartridges
│   └── cartridges.json         # Python Architecture, Cardiology, Acoustics
├── LICENSE                     # Apache 2.0 Open Source License
└── README.md                   # This document
```

---

## ⚡ Quick Start

### 1. C++ Header-Only Engine
Include the header directly into any C++17 embedded or desktop project:
```cpp
#include "otm_engine.hpp"
```

### 2. Python Reference Benchmarks
Run the empirical validation suite:
```bash
cd python_mesh
python run_full_suite.py
```

### 3. Interactive Web & PWA Harness
Open `web_harness/index.html` in any browser or visit the live deployment at [bananamilk.vercel.app](https://bananamilk.vercel.app).

---

## 📊 Empirical Benchmarks

| Metric | Project Brahmaand | Jev (TypeSafe AI) | LLaMA-3.2-1B (Edge) |
| :--- | :--- | :--- | :--- |
| **Inference Cost** | **$0.00 (Local)** | $0.042 / 1M tokens | $0.00 (Requires Cloud/GPU) |
| **Inference Latency** | **4.2 μs** (x86) / **18.7 μs** (M4) | ~12.0 ms | 45.0 ms |
| **Multiplication Ops** | **0 (Bitshift only)** | Dense Floating Point | Millions of FP16 MACs |
| **Cold Start / Load** | **< 1.2 ms (mmap)** | Cloud Network RTT | 1.8 s - 4.2 s |
| **Memory Footprint** | **840 KB** | Remote Cloud Host | 2.4 GB |
| **Factual Hallucination** | **0.0%** (Deterministic) | Model-dependent | 14.2% - 22.0% |

---

## 📜 Citation

If you build upon or reference Project Brahmaand in your research, please cite the preprint:

```bibtex
@misc{chandramouli2026brahmaand,
  author       = {Chandramouli},
  title        = {Project Brahmaand: Sovereign, Non-Autoregressive Edge Intelligence via 24-Dimensional Topological Cartridges, Zero-Multiplication Subtractive Meshes, and Predictive B-Frames},
  year         = {2026},
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.22800741},
  url          = {https://doi.org/10.5281/zenodo.22800741}
}
```

---

## ⚖️ License & Commercial Rights

* **Code & Software**: **[Business Source License 1.1 (BSL 1.1)](LICENSE)**
  * **Free & Open**: Free for academic research, education, evaluation, non-commercial use, and local experimentation.
  * **Commercial Use**: Commercial production SaaS, proprietary forks, or enterprise deployments require a commercial license from [Dr. Changmaulee Labs](mailto:yellowbridgeconnections@gmail.com).
  * **Change Date**: Transitions to Apache 2.0 on `2030-01-01`.
* **Research Paper & Documentation**: [Creative Commons Attribution 4.0 International (CC-BY-4.0)](https://creativecommons.org/licenses/by/4.0/)
