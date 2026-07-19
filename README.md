# py_img_scaler

[![Tests](https://github.com/ManuelSaleta/py-img-scaler/actions/workflows/python-test.yml/badge.svg)](https://github.com/ManuelSaleta/py-img-scaler/actions/workflows/python-test.yml)

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

```bash
    make venv      - Create a clean local virtual environment using $(PYTHON_BIN)"
    make install   - Upgrade core tooling and install platform-specific packages"
    make run       - Execute py_img_scaler main loop"
    make clean     - Destroy virtual environment and cached bytecodes"
    make lint      - Runs, Black, Ruff, and MyPy checks"
    make check     - Only check Black, Ruff, and MyPy checks"
    make test      - Run all unit tests inside the tests directory"
```

---

## Usage Examples

### 1. Command-Line Interface (CLI)

#### CLI Arguments Matrix

| Short Flag | Long Flag       | Description                                       | Default / Allowed Values |
| :--------- | :-------------- | :------------------------------------------------ | :----------------------- |
| `-s`       | `--source`      | Path to the directory containing input images.    | _Required_               |
| `-d`       | `--destination` | Path to the directory for upscaled assets.        | _Required_               |
| `-m`       | `--model`       | Select target `torchsr` architecture scale depth. | `0`, `1`, or `2`         |
| `-W`       | `--width`       | Force target width bounding configuration.        | `1920`                   |
| `-H`       | `--height`      | Force target height bounding configuration.       | `1080`                   |

Once your environment is provisioned, invoke the processing pipeline directly using explicit configuration flags:

```bash
    # Basic execution utilizing default resolutions
    py_img_scaler --source ./input_photos --destination ./upscaled_output --model 1

    # Advanced execution overriding targets for a crisp 5K Ultra-Wide frame canvas
    py_img_scaler -s ./wallpapers -d ./output -m 2 -W 5120 -H 2160
```

### 2. Working with the API Directly

```python
import logging
from src.py_img_scaler import AIUpscaler, ContextConfiguration, setup_logging

# 1. Attach your application context to the logging stream
setup_logging()
logger = logging.getLogger("py_img_scaler.core")

# 2. Build your configuration layer context matrix
config = ContextConfiguration(
    model="1",  # NinaSR-B1 architecture pipeline footprint
    tile_size=400,  # Slicing chunk constraints to prevent VRAM crashes
    target_width=5120,  # Target 5K Wide aspect dimension matching
    target_height=2160  # Target 2160p height matching
)

try:
    # 3. Instantiate the execution engine (Auto-detects CUDA / MPS / CPU)
    # Will work on all platforms MacOS / Windows / Linux
    engine = AIUpscaler(config=config)

    # 4. Ingest and upscale individual physical media frames
    success = engine.upscale_img(
        input_path="./input_photos/raw_horizon.jpg",
        output_path="./output_upscaled_photos/5k_horizon.jpg"
    )

    if success:
        logger.info("Image upscale task executed successfully.")

except ValueError as e:
    logger.error(f"Configuration boundary violation detected: {e}")
except Exception as e:
    logger.exception(f"Engine processing crash: {e}")
```

## License

- This project is open-source software licensed under the **GNU General Public License v3.0 (GPLv3)**.

### Key Terms & Copyleft Requirements:

- See the accompanying `LICENSE` file at the root of this repository for the full legal text.
