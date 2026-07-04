from dotenv import load_dotenv
from .logging_config import setup_logging
from .Image_directory_config import ImageDirectoryConfig

# Automatically search for and load a local .env file
load_dotenv()

# Initialize logging and capture the root engine instance
logger = setup_logging()

# Instantiate the Singleton instance relative to the project root
dir_config = ImageDirectoryConfig(relative=True)