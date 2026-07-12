import logging
import os
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger("py_img_scaler.config")


@dataclass(frozen=True)
class DirConfig:
    """Immutable data container for the finalized directory and model configuration."""

    source_dir: Path
    destination_dir: Path
    model_choice: str

    def get_image_files(self) -> list[Path]:
        """
        Scans the source directory and filters for supported image files.
        Enforces file-only iteration to safely avoid directory structural errors.
        """
        supported_formats = {".png", ".jpg", ".jpeg", ".webp"}

        if not self.source_dir.exists():
            return []

        return [f for f in self.source_dir.iterdir() if f.is_file() and f.suffix.lower() in supported_formats]

    def ensure_directories_exist(self) -> None:
        """Ensures that the configured source and destination folders exist."""
        self.source_dir.mkdir(parents=True, exist_ok=True)
        self.destination_dir.mkdir(parents=True, exist_ok=True)


def build_runtime_config(cli_args, relative: bool = False) -> DirConfig:
    """
    Factory function that establishes configuration hierarchy (SRP Compliant).
    Priority: 1. CLI Args -> 2. Environment Variables -> 3. Defaults
    """

    # /home/user/root/                     <─── parents[2] (Two levels above config/)
    # └── py_img_scaler/                   <─── parents[1] (One level above config/)
    #     └── config/                      <─── parents[0] (The directory containing the file)
    #         └── dir_config.py <─── Path(__file__) (The file itself)
    root_dir_pos = 2

    base_path = Path(__file__).resolve().parents[root_dir_pos] if relative else Path.cwd()

    # 1. Resolve Source Directory
    raw_source = cli_args.source or os.getenv("PYIMG_SOURCE_DIR") or "input_photos"
    src_path = Path(raw_source)
    final_source = (base_path / src_path).resolve() if relative and not src_path.is_absolute() else src_path.resolve()

    # 2. Resolve Destination Directory
    raw_dest = cli_args.destination or os.getenv("PYIMG_DEST_DIR") or "output_upscaled_photos"
    dest_path = Path(raw_dest)
    final_dest = (base_path / dest_path).resolve() if relative and not dest_path.is_absolute() else dest_path.resolve()

    # 3. Resolve Model Choice (Defaults to "0" if not provided anywhere)
    final_model = cli_args.model or os.getenv("PYIMG_MODEL") or "0"

    config = DirConfig(source_dir=final_source, destination_dir=final_dest, model_choice=final_model)

    logger.info(
        f"Config Locked -> Source: {config.source_dir} | "
        f"Destination: {config.destination_dir} | "
        f"Model: ninasr_b{config.model_choice}"
    )
    return config
