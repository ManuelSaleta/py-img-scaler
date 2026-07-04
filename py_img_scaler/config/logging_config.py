import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


def setup_logging():
    """
    Sets up a dual-destination logging pipeline for py_img_scaler.
    Outputs to both the console (sys.stdout) and a rotating log file.
    """
    logger = logging.getLogger("py_img_scaler")

    # Set the global minimum logging level
    logger.setLevel(logging.DEBUG)

    # Prevent adding duplicate handlers if this initialization function is called twice
    if logger.handlers:
        return logger

    # A clean, standardized layout tracking: Timestamp | Severity | File/Line | Message
    log_format = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d]: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 1. Console Handler (For real-time scanning in your terminal or PyCharm run window)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_format)
    logger.addHandler(console_handler)

    # 2. Rotating File Handler (Keeps up to three 5MB logs, discarding the oldest automatically)
    log_file_path = Path("upscaler.log")
    file_handler = RotatingFileHandler(
        log_file_path,
        maxBytes=5 * 1024 * 1024,  # 5 Megabytes
        backupCount=3,
        encoding="utf-8"
    )
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    return logger