from dotenv import load_dotenv

from .cmd_args_config import get_parsed_args
from .Image_directory_config import ImageDirectoryConfig
from .logging_config import setup_logging

# Automatically search for and load a local .env file
load_dotenv()

# Initialize logging and capture the root engine instance
logger = setup_logging()

# Instantiate the Singleton instance relative to the project root
dir_config = ImageDirectoryConfig(relative=True)

__all__ = ["logger", "dir_config", "get_parsed_args"]
