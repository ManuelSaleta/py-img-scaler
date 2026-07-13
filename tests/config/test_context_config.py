import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from py_img_scaler.config.context_config import ContextConfiguration


@patch("dotenv.load_dotenv")  # Globally safely mock out file system .env disk sweeps
class ContextConfigurationUnitTests(unittest.TestCase):

    def setUp(self):
        # Set up a clean mock object before every test run simulating argparse namespaces
        self.mock_cli_args = MagicMock()
        self.mock_cli_args.source = None
        self.mock_cli_args.destination = None
        self.mock_cli_args.model = None
        self.mock_cli_args.tile_size = None
        self.mock_cli_args.width = None
        self.mock_cli_args.height = None

    @patch("pathlib.Path.exists", return_value=False)
    def test_get_image_files_returns_empty_list_if_dir_does_not_exist(self, mock_exists, mock_load_dotenv):
        # Arrange
        config = ContextConfiguration(
            source_dir=Path("/fake/dir"),
            destination_dir=Path("/fake/out"),
            model="0",
        )

        # Act
        result = config.get_image_files()

        # Assert
        self.assertEqual(result, [])

    @patch("pathlib.Path.exists", return_value=True)
    @patch("pathlib.Path.iterdir")
    def test_get_image_files_filters_supported_formats_and_ignores_directories(self, mock_iterdir, mock_exists, mock_load_dotenv):
        # Arrange
        mock_png = MagicMock(spec=Path)
        mock_png.is_file.return_value = True
        mock_png.suffix = ".png"

        mock_jpeg = MagicMock(spec=Path)
        mock_jpeg.is_file.return_value = True
        mock_jpeg.suffix = ".JPEG"  # Testing case insensitivity

        mock_txt = MagicMock(spec=Path)
        mock_txt.is_file.return_value = True
        mock_txt.suffix = ".txt"

        mock_sub_dir = MagicMock(spec=Path)
        mock_sub_dir.is_file.return_value = False
        mock_sub_dir.suffix = ".png"  # Folder named fake.png

        mock_iterdir.return_value = [mock_png, mock_jpeg, mock_txt, mock_sub_dir]

        config = ContextConfiguration(
            source_dir=Path("/fake/dir"),
            destination_dir=Path("/fake/out"),
            model="0",
        )

        # Act
        result = config.get_image_files()

        # Assert
        self.assertEqual(len(result), 2)
        self.assertIn(mock_png, result)
        self.assertIn(mock_jpeg, result)
        self.assertNotIn(mock_txt, result)
        self.assertNotIn(mock_sub_dir, result)

    def test_invalid_model_choice_raises_value_error(self, mock_load_dotenv):
        # Assert post-init validation checks catch bad models
        with self.assertRaises(ValueError):
            ContextConfiguration(
                source_dir=Path("/fake/dir"),
                destination_dir=Path("/fake/out"),
                model="5"  # Invalid Choice
            )

    def test_post_init_sanitizes_negative_and_string_primitives(self, mock_load_dotenv):
        # Arrange & Act
        config = ContextConfiguration(
            source_dir=Path("/fake/dir"),
            destination_dir=Path("/fake/out"),
            model="1",
            tile_size="-300",
            target_width="3840",
            target_height=-1600
        )

        # Assert strict normalization and cast assignments work on the frozen layout
        self.assertEqual(config.tile_size, 300)
        self.assertEqual(config.target_width, 3840)
        self.assertEqual(config.target_height, 1600)

    @patch.dict(
        "os.environ",
        {
            "PYIMG_SOURCE_DIR": "./env_src",
            "PYIMG_DEST_DIR": "./env_dest",
            "PYIMG_MODEL": "1",
        },
    )
    def test_priority_1_explicit_kwargs_take_ultimate_precedence(self, mock_load_dotenv):
        # Arrange
        self.mock_cli_args.source = "./cli_src"
        self.mock_cli_args.destination = "./cli_dest"
        self.mock_cli_args.model = "2"

        # Act
        config = ContextConfiguration.from_runtime(
            cli_args=self.mock_cli_args,
            relative=False,
            source_dir="./explicit_src",
            model="0"
        )

        # Assert
        self.assertEqual(config.source_dir, Path("./explicit_src").resolve())
        self.assertEqual(config.destination_dir, Path("./cli_dest").resolve()) # CLI drops back below explicit
        self.assertEqual(config.model, "0")

    @patch.dict(
        "os.environ",
        {
            "PYIMG_SOURCE_DIR": "./env_src",
            "PYIMG_DEST_DIR": "./env_dest",
            "PYIMG_MODEL": "1",
        },
    )
    def test_priority_2_cli_args_take_precedence_over_env_vars(self, mock_load_dotenv):
        # Arrange
        self.mock_cli_args.source = "./cli_src"
        self.mock_cli_args.destination = "./cli_dest"
        self.mock_cli_args.model = "2"

        # Act
        config = ContextConfiguration.from_runtime(cli_args=self.mock_cli_args, relative=False)

        # Assert
        self.assertEqual(config.source_dir, Path("./cli_src").resolve())
        self.assertEqual(config.destination_dir, Path("./cli_dest").resolve())
        self.assertEqual(config.model, "2")

    @patch.dict(
        "os.environ",
        {
            "PYIMG_SOURCE_DIR": "./env_src",
            "PYIMG_DEST_DIR": "./env_dest",
            "PYIMG_MODEL": "1",
            "PYIMG_WIDTH": "2560",
        },
    )
    def test_priority_3_env_vars_used_if_no_cli_or_explicit_args(self, mock_load_dotenv):
        # Act
        config = ContextConfiguration.from_runtime(cli_args=self.mock_cli_args, relative=False)

        # Assert
        self.assertEqual(config.source_dir, Path("./env_src").resolve())
        self.assertEqual(config.destination_dir, Path("./env_dest").resolve())
        self.assertEqual(config.model, "1")
        self.assertEqual(config.target_width, 2560)

    @patch.dict("os.environ", {}, clear=True)
    def test_priority_4_fallback_to_defaults(self, mock_load_dotenv):
        # Act
        config = ContextConfiguration.from_runtime(cli_args=self.mock_cli_args, relative=False)

        # Assert
        self.assertEqual(config.source_dir, Path("input_photos").resolve())
        self.assertEqual(config.destination_dir, Path("output_upscaled_photos").resolve())
        self.assertEqual(config.model, "1")
        self.assertEqual(config.target_width, 1920)
        self.assertEqual(config.target_height, 1080)

    def test_absolute_path_resolution_when_not_relative(self, mock_load_dotenv):
        # Arrange
        self.mock_cli_args.source = "src_folder"

        # Act
        config = ContextConfiguration.from_runtime(cli_args=self.mock_cli_args, relative=False)

        # Assert
        expected_path = (Path.cwd() / "src_folder").resolve()
        self.assertEqual(config.source_dir, expected_path)

    def test_relative_path_resolution_using_file_parents(self, mock_load_dotenv):
        # Arrange
        self.mock_cli_args.source = "src_folder"

        # Act
        config = ContextConfiguration.from_runtime(cli_args=self.mock_cli_args, relative=True)

        # Assert
        project_root = Path(__file__).resolve().parents[2]
        expected_path = (project_root / "src_folder").resolve()
        self.assertEqual(config.source_dir, expected_path)

    @patch.object(Path, "mkdir")
    def test_ensure_directories_exist(self, mock_mkdir, mock_load_dotenv):
        # Arrange
        config = ContextConfiguration(
            source_dir=Path("/tmp/src"),
            destination_dir=Path("/tmp/dest"),
            model="1",
        )

        # Act
        config.ensure_directories_exist()

        # Assert
        self.assertEqual(mock_mkdir.call_count, 2)
        mock_mkdir.assert_any_call(parents=True, exist_ok=True)


if __name__ == "__main__":
    unittest.main()