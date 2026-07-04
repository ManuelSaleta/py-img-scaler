import sys
import time

# --- Monkeypatch basicsr / torchvision breaking change ---
import torchvision
import torchvision.transforms.functional as TVF

try:
    from torchvision.transforms import functional_tensor
except ImportError:
    import types

    sys.modules['torchvision.transforms.functional_tensor'] = TVF
# ---------------------------------------------------------

# Import BOTH the directory configuration and the active logger instance
from py_img_scaler.config import dir_config, logger
from py_img_scaler.core.upscaler import AIUpscaler


def main():
    logger.info("================ Starting PyImgScaler Execution ================")

    # Use the config abstraction to verify/create directories
    dir_config.ensure_directories_exist()

    supported_formats = {'.png', '.jpg', '.jpeg', '.webp'}

    # Enforce file-only iteration to safely avoid directory structural errors
    image_files = [
        f for f in dir_config.source_dir.iterdir()
        if f.is_file() and f.suffix.lower() in supported_formats
    ]

    if not image_files:
        logger.warning(f"No valid images found in '{dir_config.source_dir}'. Add images there and re-run!")
        return

    start_time = time.time()
    upscaler_engine = AIUpscaler(model_name="RealESRGAN_x4plus", tile_size=400)

    success_count = 0
    for idx, file_path in enumerate(image_files, 1):
        logger.info(f"Queue Progress: [{idx}/{len(image_files)}]")

        # Output maps straight to config space
        out_path = dir_config.destination_dir / f"5k_{file_path.name}"

        success = upscaler_engine.upscale_to_5k(file_path, out_path)
        if success:
            success_count += 1

    total_time = time.time() - start_time
    logger.info(f"Execution complete. Processed: {success_count}/{len(image_files)} files in {total_time:.2f}s.")
    logger.info("=====================================================================")


if __name__ == "__main__":
    main()