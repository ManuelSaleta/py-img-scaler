import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from py_img_scaler.config.dir_config import (
    DirConfig,
    build_runtime_config,
)


class DirConfigUnitTests(unittest.TestCase):

    def setUp(self):
        # Set up a clean mock object before every test run
        self.mock_cli_args = MagicMock()
        self.mock_cli_args.source = None
        self.mock_cli_args.destination = None
        self.mock_cli_args.model = None

    @patch("pathlib.Path.exists", return_value=False)
    def test_get_image_files_returns_empty_list_if_dir_does_not_exist(self, mock_exists):
        # Arrange
        config = DirConfig(
            source_dir=Path("/fake/dir"),
            destination_dir=Path("/fake/out"),
            model_choice="0",
        )

        # Act
        result = config.get_image_files()

        # Assert
        self.assertEqual(result, [])

    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.iterdir")
    def test_get_image_files_filters_supported_formats_and_ignores_directories(self, mock_iterdir, mock_exists):
        # Arrange
        # Create mock file paths with fake attributes
        mock_png = MagicMock(spec=Path)
        mock_png.is_file.return_value = True
        mock_png.suffix = ".png"

        mock_jpeg = MagicMock(spec=Path)
        mock_jpeg.is_file.return_value = True
        mock_jpeg.suffix = ".JPEG"  # Testing uppercase normalization (.lower())

        mock_txt = MagicMock(spec=Path)
        mock_txt.is_file.return_value = True
        mock_txt.suffix = ".txt"  # Unsupported format

        mock_sub_dir = MagicMock(spec=Path)
        mock_sub_dir.is_file.return_value = False  # Is a directory, not a file
        mock_sub_dir.suffix = ".png"  # Sneaky directory named 'folder.png'

        # Set iterdir to yield our mixed batch of items
        mock_iterdir.return_value = [mock_png, mock_jpeg, mock_txt, mock_sub_dir]

        config = DirConfig(
            source_dir=Path("/fake/dir"),
            destination_dir=Path("/fake/out"),
            model_choice="0",
        )

        # Act
        result = config.get_image_files()

        # Assert
        # Should only contain the valid PNG and JPEG files
        self.assertEqual(len(result), 2)
        self.assertIn(mock_png, result)
        self.assertIn(mock_jpeg, result)
        self.assertNotIn(mock_txt, result)
        self.assertNotIn(mock_sub_dir, result)

    @patch.dict(
        "os.environ",
        {
            "PYIMG_SOURCE_DIR": "./env_src",
            "PYIMG_DEST_DIR": "./env_dest",
            "PYIMG_MODEL": "1",
        },
    )
    def test_priority_1_cli_args_take_precedence(self):
        # Arrange
        self.mock_cli_args.source = "./cli_src"
        self.mock_cli_args.destination = "./cli_dest"
        self.mock_cli_args.model = "2"

        # Act
        config = build_runtime_config(self.mock_cli_args, relative=False)

        # Assert
        self.assertEqual(config.source_dir, Path("./cli_src").resolve())
        self.assertEqual(config.destination_dir, Path("./cli_dest").resolve())
        self.assertEqual(config.model_choice, "2")

    @patch.dict(
        "os.environ",
        {
            "PYIMG_SOURCE_DIR": "./env_src",
            "PYIMG_DEST_DIR": "./env_dest",
            "PYIMG_MODEL": "1",
        },
    )
    def test_priority_2_env_vars_used_if_no_cli_args(self):
        # Act
        config = build_runtime_config(self.mock_cli_args, relative=False)

        # Assert
        self.assertEqual(config.source_dir, Path("./env_src").resolve())
        self.assertEqual(config.destination_dir, Path("./env_dest").resolve())
        self.assertEqual(config.model_choice, "1")

    # We patch a completely clear environment to force the fallback defaults
    @patch.dict("os.environ", {}, clear=True)
    def test_priority_3_fallback_to_defaults(self):
        # Act
        config = build_runtime_config(self.mock_cli_args, relative=False)

        # Assert
        self.assertEqual(config.source_dir, Path("input_photos").resolve())
        self.assertEqual(config.destination_dir, Path("output_upscaled_photos").resolve())
        self.assertEqual(config.model_choice, "0")

    def test_absolute_path_resolution_when_not_relative(self):
        # Arrange
        self.mock_cli_args.source = "src_folder"

        # Act
        config = build_runtime_config(self.mock_cli_args, relative=False)

        # Assert
        expected_path = (Path.cwd() / "src_folder").resolve()
        self.assertEqual(config.source_dir, expected_path)

    def test_relative_path_resolution_using_file_parents(self):
        # Arrange
        self.mock_cli_args.source = "src_folder"

        # Act
        config = build_runtime_config(self.mock_cli_args, relative=True)

        # Assert
        project_root = Path(__file__).resolve().parents[2]
        expected_path = (project_root / "src_folder").resolve()
        self.assertEqual(config.source_dir, expected_path)

    @patch.object(Path, "mkdir")
    def test_ensure_directories_exist(self, mock_mkdir):
        # Arrange
        config = DirConfig(
            source_dir=Path("/tmp/src"),
            destination_dir=Path("/tmp/dest"),
            model_choice="0",
        )

        # Act
        config.ensure_directories_exist()

        # Assert
        self.assertEqual(mock_mkdir.call_count, 2)
        mock_mkdir.assert_any_call(parents=True, exist_ok=True)


if __name__ == "__main__":
    unittest.main()
