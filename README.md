# py_img_scaler

[![Tests](https://github.com/ManuelSaleta/py-img-scaler/actions/workflows/python-test.yml/badge.svg)](https://github.com/ManuelSaleta/py-img-scaler/actions/workflows/python-test.yml)

A cross-platform, high-performance image upscaling tool, leverages AI image processing.

Powered natively by `torchsr` (NinaSR).

---

## Features

- **Cross-Platform Acceleration:** Native support for NVIDIA CUDA, AMD ROCm (Linux via HIP), and Apple Silicon (macOS via MPS).
- **VRAM Safety:** Smart local tiling/patching with edge-padding blending to prevent Out-of-Memory (OOM) errors on large files.

---

## Prerequisites & Installation

### 1. System Dependencies (Linux)

Ensure Python 3.13 (recommended) and your platform graphics drivers (ROCm/CUDA) are installed.

### 2. Automated Environment Setup

The project contains a platform-aware pipeline configuration tracker. Run the following command to completely clean, generate the virtual environment, and map the correct vendor binaries for your host OS:

```bash
make fresh
```

### Additional Make recipes

```bash
    make venv         - Create a clean local virtual environment using $(PYTHON_BIN)
    make install      - Upgrade core tooling and install platform-specific packages
    make install-dev  - Install dev dependencies like ruff, pytest etc.
    make run          - Execute py_img_scaler main loop
    make clean        - Destroy virtual environment and cached bytecodes
    make lint         - Runs, Black, Ruff, and MyPy checks
    make check        - Only check Black, Ruff, and MyPy checks
    make test         - Run all unit tests inside the tests directory
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
### 2. Simple Configuation
```python
from py_img_scaler import ImgScaler, ContextConfiguration

# 1. Use the factory to load defaults (or .env file variables)
# This auto-sets resolution, model, and tile sizes to safe defaults.
config = ContextConfiguration.from_runtime()

# 2. Instantiate and run
engine = ImgScaler(config=config)
engine.upscale_img(
    input_path="./my_photo.jpg",
    output_path="./upscaled_photo.jpg"
)
```
### 3. Advanced Configuration 

```python
import logging
from pathlib import Path
from src.py_img_scaler import ImgScaler, ContextConfiguration, setup_logging

# 1. Attach your application context to the logging stream
setup_logging()
logger = logging.getLogger("py_img_scaler.core")


# 2. Build a custom configuration matrix
config = ContextConfiguration(
    model="1",                          # Options: "0", "1", "2" - 3 is most demanding model
    tile_size=400,                      # Adjust lower if you encounter VRAM Out-Of-Memory errors
    target_width=5120,                  # Adjust your upscaling target width
    target_height=2160,                 # Adjust your upscaling target height
    source_dir=Path("./input"),         # Input dir containing your images.
    destination_dir=Path("./output")    # Destination dir
)

# 3. Instantiate the engine (Auto-detects CUDA / MPS / CPU)
engine = ImgScaler(config=config)

# 4. Upscale images
engine.upscale_img("./input/raw_horizon.jpg", "./output/5k_horizon.jpg")
```

## License

- This project is open-source software licensed under the **GNU General Public License v3.0 (GPLv3)**.

### Key Terms & Copyleft Requirements:

- See the accompanying `LICENSE` file at the root of this repository for the full legal text.
