import os
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger("py_img_scaler.config")


@dataclass(frozen=True)
class ContextConfiguration:
    """
    Unified configuration context for py_img_scaler.
    Resolves configuration across Explicit Arguments -> CLI Namespace -> ENV Variables -> Defaults.
    """
    source_dir: Path
    destination_dir: Path
    model: str = "1"
    tile_size: int = 400
    target_width: int = 1920
    target_height: int = 1080

    def __post_init__(self):
        """Validates and sanitizes parameters post-construction."""
        if self.model not in ["0", "1", "2"]:
            raise ValueError(f"Model '{self.model}' is invalid. Choose from 0, 1, or 2.")

        # Ensure strict data types and absolute paths via object manipulation on frozen instance
        object.__setattr__(self, "tile_size", int(abs(int(self.tile_size))))
        object.__setattr__(self, "target_width", int(abs(int(self.target_width))))
        object.__setattr__(self, "target_height", int(abs(int(self.target_height))))
        object.__setattr__(self, "source_dir", Path(self.source_dir).resolve())
        object.__setattr__(self, "destination_dir", Path(self.destination_dir).resolve())

        logger.info(
            f"Config Locked -> Source: {self.source_dir} | "
            f"Destination: {self.destination_dir} | "
            f"Model: ninasr_b{self.model} | "
            f"Resolution: {self.target_width}x{self.target_height}"
        )

    @classmethod
    def from_runtime(cls, cli_args: Any = None, relative: bool = False, **kwargs) -> "ContextConfiguration":
        """
        Factory method serving as the single entry point for all configuration.
        Priority: Explicit kwargs > CLI arguments > Environment Variables > Defaults
        """
        # Load environment variables right here so programmatic users get seamless
        # .env parsing out of the box without needing external boilerplate.
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            # Fallback safeguard if a programmatic user didn't install python-dotenv
            logger.debug("python-dotenv not found; skipping automated .env parsing.")

        # Resolve base path context
        root_dir_pos = 2
        base_path = Path(__file__).resolve().parents[root_dir_pos] if relative else Path.cwd()

        # Helper to extract value down the priority chain
        def resolve_val(key: str, env_var: str, default: Any, cli_attr: str | None = None) -> Any:
            # 1. Check explicit keyword args (programmatic use / hardcoded values)
            if key in kwargs and kwargs[key] is not None:
                return kwargs[key]
            # 2. Check CLI arguments object if provided
            if cli_args and cli_attr and hasattr(cli_args, cli_attr) and getattr(cli_args, cli_attr) is not None:
                return getattr(cli_args, cli_attr)
            # 3. Check Environment Variables
            return os.getenv(env_var) or default

        # Resolve paths
        raw_source = resolve_val("source_dir", "PYIMG_SOURCE_DIR", "input_photos", "source")
        src_path = Path(raw_source)
        final_source = base_path / src_path if relative and not src_path.is_absolute() else src_path

        raw_dest = resolve_val("destination_dir", "PYIMG_DEST_DIR", "output_upscaled_photos", "destination")
        dest_path = Path(raw_dest)
        final_dest = base_path / dest_path if relative and not dest_path.is_absolute() else dest_path

        # Resolve remaining configuration primitives
        final_model = str(resolve_val("model", "PYIMG_MODEL", "1", "model"))
        final_tile = resolve_val("tile_size", "PYIMG_TILE_SIZE", 400, "tile_size")
        final_width = resolve_val("target_width", "PYIMG_WIDTH", 1920, "width")
        final_height = resolve_val("target_height", "PYIMG_HEIGHT", 1080, "height")

        return cls(
            source_dir=final_source,
            destination_dir=final_dest,
            model=final_model,
            tile_size=final_tile,
            target_width=final_width,
            target_height=final_height
        )

    def get_image_files(self) -> list[Path]:
        """Scans the source directory and filters for supported image files."""
        supported_formats = {".png", ".jpg", ".jpeg", ".webp"}
        if not self.source_dir.exists():
            return []
        return [f for f in self.source_dir.iterdir() if f.is_file() and f.suffix.lower() in supported_formats]

    def ensure_directories_exist(self) -> None:
        """Ensures that the configured source and destination folders exist."""
        self.source_dir.mkdir(parents=True, exist_ok=True)
        self.destination_dir.mkdir(parents=True, exist_ok=True)