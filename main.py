import time

from dotenv import load_dotenv

"""
ATTENTION: Extremely important note:     # 0. Very fist step, load environment variables from a .env file if present
    load_dotenv() - This ensures all custom modules have access to environment variables before any other code executes.
    Do not change the order, loading custom modules before this line could break the application if those modules rely on environment variables.
"""
load_dotenv()
from py_img_scaler.config import build_runtime_config, get_parsed_args, logger
from py_img_scaler.core import AIUpscaler


def main():
    """
    Main entry point for the py_img_scaler application.
    Handles command-line arguments, initializes the directory configuration,
    and orchestrates the upscaling of image resolutions.
    """

    # Command line args
    parsed_arguments = get_parsed_args()

    # Config for directories, image files, and rendering model
    current_config = build_runtime_config(parsed_arguments)
    current_config.ensure_directories_exist()

    # Found images
    image_files = current_config.get_image_files()

    if not image_files:
        logger.warning(
            f"No valid images found in '{current_config.source_dir}'. Add images there and re-run!"
        )
        return

    start_time = time.time()

    # Engine initialization matching your torchsr architecture configuration
    upscaler_engine = AIUpscaler(
        model_choice=current_config.model_choice, tile_size=400
    )

    success_count = 0

    logger.info("================ Starting py_img_scaler Execution ================")

    for idx, file_path in enumerate(image_files, 1):
        logger.info(f"Queue Progress: [{idx}/{len(image_files)}]")

        # Output maps straight to config space
        out_path = current_config.destination_dir / f"5k_{file_path.name}"

        success = upscaler_engine.upscale_img(file_path, out_path)
        if success:
            success_count += 1

    total_time = time.time() - start_time
    logger.info(
        f"Execution complete. Processed: {success_count}/{len(image_files)} files in {total_time:.2f}s."
    )
    logger.info("=====================================================================")


if __name__ == "__main__":
    main()
