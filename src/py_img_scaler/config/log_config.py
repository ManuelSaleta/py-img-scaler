import logging
import os
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path


class ImgUpLogger:
    def __init__(self, name: str = "py_img_scaler", log_level: int = logging.INFO, log_dir: str = "logs"):
        self.logger = logging.getLogger(name)
        self.log_dir = Path(log_dir)

        # Determine log level (Env var takes precedence)
        env_level = os.getenv("LOG_LEVEL")
        self.level = getattr(logging, env_level.upper()) if env_level else log_level

        self._configure()

    def _configure(self):
        """Internal setup to avoid duplicate handlers."""
        if self.logger.handlers:
            return

        self.logger.setLevel(self.level)
        self.log_dir.mkdir(exist_ok=True)

        # Formatter
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Console Handler
        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(formatter)
        self.logger.addHandler(console)

        # File Handler
        log_file = self.log_dir / f"upscaler_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.log"
        file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=3, encoding="utf-8")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def get(self) -> logging.Logger:
        return self.logger
