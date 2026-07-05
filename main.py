import argparse
import sys
import time

from py_img_scaler.config import dir_config, logger, TargetResolution
from py_img_scaler.core.upscaler import AIUpscaler


def main():
    """
    Main entry point for the PyImgScaler application.
    Handles command-line arguments, initializes the directory configuration,
    and orchestrates the upscaling of image resolutions.
    """
    # TODO: Finish implementing command-line argument parsing for source/destination directories to override config defaults
    # And turn it into a proper CLI binary with --help and usage instructions
    parser = argparse.ArgumentParser(
        description="PyImgScaler: A cross-platform AI upscaling utility to upscale images to 5K."
    )
    parser.add_argument(
        "-s", "--source",
        type=str,
        help="Path to the source directory containing input images. (Overrides config default)"
    )
    parser.add_argument(
        "-d", "--destination",
        type=str,
        help="Path to the destination directory for upscaled outputs. (Overrides config default)"
    )
    parser.add_argument(
        "--width",
        type=int,
        default=5120,
        help="Target width for the upscaled images. (Overrides config default)"
    )
    parser.add_argument(
        "--height",
        type=int,
        default=2160,
        help="Target height for the upscaled images. (Overrides config default)"
    )

    args = parser.parse_args()
    if args.source:
        dir_config.source_dir = Path(args.source)
    if args.destination:
        dir_config.destination_dir = Path(args.destination)

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

    target_resolution = TargetResolution(args.width, args.height)

    # Engine initialization matching your torchsr architecture configuration
    upscaler_engine = AIUpscaler(model_name="ninasr_b0", tile_size=400, target_resolution=target_resolution)

    success_count = 0
    for idx, file_path in enumerate(image_files, 1):
        logger.info(f"Queue Progress: [{idx}/{len(image_files)}]")

        # Output maps straight to config space
        out_path = dir_config.destination_dir / f"5k_{file_path.name}"

        success = upscaler_engine.upscale_img(file_path, out_path)
        if success:
            success_count += 1

    total_time = time.time() - start_time
    logger.info(f"Execution complete. Processed: {success_count}/{len(image_files)} files in {total_time:.2f}s.")
    logger.info("=====================================================================")


if __name__ == "__main__":
    main()
