import os
from typing import NamedTuple, Literal

class TargetResolution(NamedTuple):
    """
    Represents the target resolution for image scaling.
    """
    width: int = 5120
    height: int = 2160

class LogConfig(NamedTuple):
    """
    Represents the logging configuration for the application.
    """
    name: str = 'py_img_scaler_log'
    debug_level: Literal[10, 20] = 20  # Safe static typing for INFO/DEBUG

# class EnvironmentConfig(NamedTuple):
#     """
#     Represents the environment configuration for the application.
#     """
#     env_source_:str  = os.getenv("PYIMG_SOURCE_DIR") or "source_photos"
#     env_dest:str = os.getenv("PYIMG_DEST_DIR") or "upscaled_photos"

