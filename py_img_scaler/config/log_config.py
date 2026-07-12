import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(name="py_img_scaler", log_level=logging.INFO) -> logging.Logger:
    """
    Sets up a dual-destination logging pipeline for py_img_scaler.
    Outputs to both the console (sys.stdout) and a rotating log file.
    """
    logger = logging.getLogger(name)

    # Set the global minimum logging level
    log_level = os.getenv("LOG_LEVEL") or log_level
    logger.setLevel(log_level)

    # Prevent adding duplicate handlers if this initialization function is called twice
    if logger.handlers:
        return logger

    # A clean, standardized layout tracking: Timestamp | Severity | File/Line | Message
    log_format = logging.Formatter(
        "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # CONSOLE Handler (For real-time scanning in your terminal or PyCharm run window)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    # Format: YYYY-MM-DD_HHMMSS (e.g., upscaler_2026-07-11_114622.log)
    date_time_info = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    log_filename = f"upscaler_{date_time_info}.log"
    log_file_path = Path(log_filename)

    # FILE Handler (Keeps up to three 5MB logs, discarding the oldest automatically)
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=5 * 1024 * 1024,  # 5 Megabytes
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    return logger
