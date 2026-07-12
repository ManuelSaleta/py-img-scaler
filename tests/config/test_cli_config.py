import random
import unittest
from unittest.mock import patch

from py_img_scaler.config import cli_config

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

        # You can now access the actual exception object via context.exception
        actual_error_message = str(context.exception)

        # This is a bit brittle as you don't necessarily want to test the string values BUT...
        # It is a good example on how to extract the context for other tests
        # Verify the message matches your cli_config error output
        self.assertEqual(
            actual_error_message,
            "Model '4' is invalid. Choose from 0, 1, or 2. 0 being least resource intensive model.",
        )


if __name__ == "__main__":
    unittest.main()
