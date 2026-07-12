# py_img_scaler

A cross-platform, high-performance AI image upscaling tool.

Powered natively by `torchsr` (NinaSR). Supports hardware acceleration across NVIDIA, AMD, and Apple Silicon.

---

## Features

- **Cross-Platform Acceleration:** Native support for NVIDIA CUDA, AMD ROCm (Linux via HIP), and Apple Silicon (macOS via MPS).
- **VRAM Safety:** Smart local tiling/patching with edge-padding blending to prevent Out-of-Memory (OOM) errors on large files.

---

## Prerequisites & Installation

### 1. System Dependencies (Linux)

Ensure Python 3.14 (recommended) and your platform graphics drivers (ROCm/CUDA) are installed.

### 2. Automated Environment Setup

The project contains a platform-aware pipeline configuration tracker. Run the following command to completely clean, generate the virtual environment, and map the correct vendor binaries for your host OS:

```bash
make fresh
```

### Additional Make recipes

    `make venv`      - Create a clean local virtual environment using $(PYTHON_BIN)"
    `make install`   - Upgrade core tooling and install platform-specific packages"
    `make run`       - Execute py_img_scaler main loop"
    `make clean`     - Destroy virtual environment and cached bytecodes"
    `make lint`      - Runs, Black, Ruff, and MyPy checks"
    `make check`     - Only check Black, Ruff, and MyPy checks"

---

## License

- This project is open-source software licensed under the **GNU General Public License v3.0 (GPLv3)**.

### Key Terms & Copyleft Requirements:

- See the accompanying `LICENSE` file at the root of this repository for the full legal text.
