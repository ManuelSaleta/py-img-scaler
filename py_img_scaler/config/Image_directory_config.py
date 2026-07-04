import os
import logging
from pathlib import Path

logger = logging.getLogger("PyImgScaler")


class ImageDirectoryConfig:
    """
    Manages source and destination directories for PyImgScaler.
    Supports environment variables (great for Docker) and functions as a Singleton.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """Implements the Singleton pattern to ensure only one config exists at runtime."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, source_dir: str = None, destination_dir: str = None, relative: bool = False):
        # Guard clause to ensure initialization only runs once for the Singleton
        if getattr(self, '_initialized', False):
            return

        self.relative = relative

        # 1. Resolve paths checking Environment Variables first, then explicit arguments, then defaults
        env_source = os.getenv("PYIMG_SOURCE_DIR")
        env_dest = os.getenv("PYIMG_DEST_DIR")

        base_path = Path(__file__).resolve().parents[2] if relative else Path.cwd()

        initial_source = env_source or source_dir or "input_photos"
        initial_dest = env_dest or destination_dir or "output_upscaled_photos"

        # Initialize the actual attributes using our clean logic setter methods
        self.set_source_dir(initial_source, base_path)
        self.set_destination_dir(initial_dest, base_path)

        self._initialized = True
        logger.info(f"Directory Config Locked -> Source: {self.source_dir} | Destination: {self.destination_dir}")

    def set_source_dir(self, source_dir: str, base_path: Path = Path.cwd()):
        """Sets and normalizes the Source Directory."""
        path_obj = Path(source_dir)
        if self.relative and not path_obj.is_absolute():
            self.source_dir = (base_path / path_obj).resolve()
        else:
            self.source_dir = path_obj.resolve()

    def set_destination_dir(self, destination_dir: str, base_path: Path = Path.cwd()):
        """Sets and normalizes the Destination Directory."""
        path_obj = Path(destination_dir)
        if self.relative and not path_obj.is_absolute():
            self.destination_dir = (base_path / path_obj).resolve()
        else:
            self.destination_dir = path_obj.resolve()

    def ensure_directories_exist(self):
        """Ensures that the configured source and destination folders actually exist on the system."""
        self.source_dir.mkdir(parents=True, exist_ok=True)
        self.destination_dir.mkdir(parents=True, exist_ok=True)