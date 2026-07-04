# PyImgScaler

A cross-platform, high-performance AI image upscaling.

Powered natively by `torchsr` (NinaSR). Supports hardware acceleration across NVIDIA, AMD, and Apple Silicon.

---

## Features

- **Cross-Platform Acceleration:** Native support for NVIDIA CUDA, AMD ROCm (Linux via HIP), and Apple Silicon (macOS via MPS).
- **VRAM Safety:** Smart local tiling/patching with edge-padding blending to prevent Out-of-Memory (OOM) errors on large files.

---

## Prerequisites & Installation

### 1. System Dependencies (Linux)

Ensure Python 3.12 (recommended) and your platform graphics drivers (ROCm/CUDA) are installed.

### 2. Automated Environment Setup

The project contains a platform-aware pipeline configuration tracker. Run the following command to completely clean, generate the virtual environment, and map the correct vendor binaries for your host OS:

```bash
make fresh
```
