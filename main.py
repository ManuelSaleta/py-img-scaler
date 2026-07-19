import time

from src.py_img_scaler.config import ContextConfiguration, setup_logging, get_parsed_args
from src.py_img_scaler.core import AIUpscaler


def main():
    """
    Main entry point for the py_img_scaler application.
    Orchestrates execution using ContextConfiguration and the AIUpscaler engine.
    """
    logger = setup_logging()

    logger.info("Initializing py_img_scaler runtime environment...")

    # 1. Parse raw command line args
    parsed_arguments = get_parsed_args()

    # 2. Build configuration context (Explicitly handling the 5K target defaults here)
    current_config = ContextConfiguration.from_runtime(cli_args=parsed_arguments)
    current_config.ensure_directories_exist()

    # 3. Locate processing files
    image_files = current_config.get_image_files()

    if not image_files:
        logger.warning(f"No valid images found in '{current_config.source_dir}'. Add images there and re-run!")
        return

    start_time = time.time()

    # 4. Engine initialization accepts our single context object
    upscaler_engine = AIUpscaler(config=current_config)

    success_count = 0

    logger.info("================ Starting py_img_scaler Execution ================")

    for idx, file_path in enumerate(image_files, 1):
        logger.info(f"Queue Progress: [{idx}/{len(image_files)}]")

        # Output path names target resolution prefix dynamically from context
        prefix = f"{current_config.target_width}x{current_config.target_height}_"
        out_path = current_config.destination_dir / f"{prefix}{file_path.name}"

        success = upscaler_engine.upscale_img(file_path, out_path)
        if success:
            success_count += 1

    total_time = time.time() - start_time
    logger.info(f"Execution complete. Processed: {success_count}/{len(image_files)} files in {total_time:.2f}s.")
    logger.info("=====================================================================")


if __name__ == "__main__":
    main()
