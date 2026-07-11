import os
import unittest
from py_img_scaler.config import log_config
from unittest.mock import patch, MagicMock
import logging
# Testing Logging is not really recommended, just checking it respects the custom ENV_VARS
class LoggingConfigUnitTests(unittest.TestCase):

    def tearDown(self):
        # Clean up the logger handlers after tests so they don't leak into other test suites
        logger = logging.getLogger("py_img_scaler_test")
        logger.handlers.clear()

    # We mock RotatingFileHandler completely so it never touches the disk
    @patch("py_img_scaler.config.logging_config.RotatingFileHandler")
    @patch.dict("os.environ", {"LOG_LEVEL": "DEBUG"})
    def test_log_level_overridden_by_env_var(self, mock_file_handler):
        # Act
        logger = log_config.setup_logging(name="py_img_scaler_test", log_level=logging.INFO)

        # Assert: Even though we requested INFO, the ENV var should force DEBUG
        self.assertEqual(logger.level, logging.DEBUG)

    @patch("py_img_scaler.config.logging_config.RotatingFileHandler")
    @patch.dict("os.environ", {}, clear=True)
    def test_prevent_duplicate_handlers(self, mock_file_handler):
        # Act: Call it twice on the same logger name
        logger_first = log_config.setup_logging(name="py_img_scaler_test")
        initial_count = len(logger_first.handlers)

        logger_second = log_config.setup_logging(name="py_img_scaler_test")
        secondary_count = len(logger_second.handlers)

        # Assert: Handlers shouldn't stack up infinitely
        self.assertEqual(initial_count, 2)  # 1 Console + 1 File
        self.assertEqual(secondary_count, 2)


if __name__ == "__main__":
    unittest.main()