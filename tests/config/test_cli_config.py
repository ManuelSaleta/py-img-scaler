import random
import unittest
from unittest.mock import patch

from src.py_img_scaler.config import cli_config

# allowed values for --model, -m = 0,1,2
randomly_picked_model = str(random.randint(0, 2))


class CliConfigUnitTests(unittest.TestCase):

    # sys.argv is a static replacement, so it won't send an argument to the function.
    # Path.is_dir uses 'return_value', so it WILL send a mock argument to the function.
    @patch("pathlib.Path.is_dir", return_value=True)
    @patch("sys.argv", ["program_name", "--source", "./my_source_dir"])
    def test_source_dir_exists(self, mock_is_dir):  # Only accept the mock from Path.is_dir
        # Arrange
        desired_source_dir = "./my_source_dir"

        # Act
        parsed = cli_config.get_parsed_args()

        # Assert
        self.assertEqual(desired_source_dir, parsed.source)

    @patch("pathlib.Path.is_dir", return_value=False)
    @patch("sys.argv", ["program_name", "--source", "./invalid_dir"])
    def test_source_dir_validation_fails(self, mock_is_dir):  # Only accept the mock from Path.is_dir
        # Arrange/Act/Assert
        with self.assertRaises(ValueError):
            cli_config.get_parsed_args()

    @patch("pathlib.Path.is_dir", return_value=True)
    @patch("sys.argv", ["program_name", "--destination", "./my_detination_dir"])
    def test_destination_dir_exists(self, mock_is_dir):  # Only accept the mock from Path.is_dir
        # Arrange
        desired_destination_dir = "./my_detination_dir"

        # Act
        parsed = cli_config.get_parsed_args()

        # Assert
        self.assertEqual(desired_destination_dir, parsed.destination)

    @patch("pathlib.Path.is_dir", return_value=False)
    @patch("sys.argv", ["program_name", "--destination", "./invalid_dir"])
    def test_destination_dir_validation_fails(self, mock_is_dir):  # Only accept the mock from Path.is_dir
        # Arrange/Act/Assert
        with self.assertRaises(ValueError):
            cli_config.get_parsed_args()

    @patch("pathlib.Path.is_dir", return_value=True)
    @patch("sys.argv", ["program_name", "-s", "./my_source_dir"])
    def test_s_dir_exists(self, mock_is_dir):  # Only accept the mock from Path.is_dir
        # Arrange
        desired_source_dir = "./my_source_dir"

        # Act
        parsed = cli_config.get_parsed_args()

        # Assert
        self.assertEqual(desired_source_dir, parsed.source)

    @patch("pathlib.Path.is_dir", return_value=False)
    @patch("sys.argv", ["program_name", "-s", "./invalid_dir"])
    def test_s_dir_validation_fails(self, mock_is_dir):  # Only accept the mock from Path.is_dir
        # Arrange/Act/Assert
        with self.assertRaises(ValueError):
            cli_config.get_parsed_args()

    @patch("pathlib.Path.is_dir", return_value=True)
    @patch("sys.argv", ["program_name", "-d", "./my_detination_dir"])
    def test_d_dir_exists(self, mock_is_dir):  # Only accept the mock from Path.is_dir
        # Arrange
        desired_destination_dir = "./my_detination_dir"

        # Act
        parsed = cli_config.get_parsed_args()

        # Assert
        self.assertEqual(desired_destination_dir, parsed.destination)

    @patch("pathlib.Path.is_dir", return_value=False)
    @patch("sys.argv", ["program_name", "-d", "./invalid_dir"])
    def test_d_dir_validation_fails(self, mock_is_dir):  # Only accept the mock from Path.is_dir
        # Arrange/Act/Assert
        with self.assertRaises(ValueError):
            cli_config.get_parsed_args()

    @patch("pathlib.Path.is_dir", return_value=True)
    @patch("sys.argv", ["program_name", "--model", randomly_picked_model])
    def test_only_allowed_val_for_model(self, mock_is_dir):  # Only accept the mock from Path.is_dir
        # Arrange
        allowed_models = ["0", "1", "2"]

        # Act
        parsed = cli_config.get_parsed_args()

        # Assert
        self.assertEqual(parsed.model in allowed_models, True)

    @patch("pathlib.Path.is_dir", return_value=True)
    @patch("sys.argv", ["program_name", "-m", randomly_picked_model])
    def test_only_allowed_val_for_m(self, mock_is_dir):  # Only accept the mock from Path.is_dir
        # shortcut -m for --model

        # Arrange
        allowed_models = ["0", "1", "2"]

        # Act
        parsed = cli_config.get_parsed_args()

        # Assert
        self.assertEqual(parsed.model in allowed_models, True)

    @patch("pathlib.Path.is_dir", return_value=False)
    @patch("sys.argv", ["program_name", "--model", "4"])
    def test_fails_unsupported_model(self, mock_is_dir):  # Only accept the mock from Path.is_dir
        # Arrange/Act/Assert
        with self.assertRaises(ValueError):
            cli_config.get_parsed_args()

    @patch("pathlib.Path.is_dir", return_value=False)
    @patch("sys.argv", ["program_name", "-m", "4"])
    def test_fails_unsupported_m(self, mock_is_dir):
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            cli_config.get_parsed_args()

        # Extract the exception context message string
        actual_error_message = str(context.exception)

        # Verify the message matches your cli_config error output
        self.assertEqual(
            actual_error_message,
            "Model '4' is invalid. Choose from 0, 1, or 2. 0 being least resource intensive model.",
        )

    @patch("pathlib.Path.is_dir", return_value=True)
    @patch("sys.argv", ["program_name", "--width", "3840", "--height", "2160"])
    def test_width_and_height_long_arguments(self, mock_is_dir):
        """Verify long flags cleanly map primitives down to targets."""
        # Act
        parsed = cli_config.get_parsed_args()

        # Assert
        self.assertEqual(parsed.width, 3840)
        self.assertEqual(parsed.height, 2160)

    @patch("pathlib.Path.is_dir", return_value=True)
    @patch("sys.argv", ["program_name", "-W", "2560", "-H", "-1440"])
    def test_width_and_height_short_flags_with_negative_sanitization(self, mock_is_dir):
        """Confirm negative input configurations sanitize via validation math layers."""
        # Act
        parsed = cli_config.get_parsed_args()

        # Assert
        self.assertEqual(parsed.width, 2560)
        self.assertEqual(parsed.height, 1440)  # -1440 should be sanitized via abs() to 1440

    @patch("pathlib.Path.is_dir", return_value=True)
    @patch("sys.argv", ["program_name"])
    def test_width_and_height_fallback_to_none_when_unspecified(self, mock_is_dir):
        """Verify dimension arguments resolve cleanly to None if left out entirely."""
        # Act
        parsed = cli_config.get_parsed_args()

        # Assert
        self.assertIsNone(parsed.width)
        self.assertIsNone(parsed.height)


if __name__ == "__main__":
    unittest.main()