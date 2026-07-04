import os
import cv2
import torch
import logging
import urllib.request
from pathlib import Path
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer

# Retrieve the pre-configured global application logger
logger = logging.getLogger("PyImgScaler")


class AIUpscaler:
    def __init__(self, model_name="RealESRGAN_x4plus", tile_size=400):
        """
        Cross-platform AI engine supporting CUDA (Linux), MPS (macOS), and CPU fallback.
        """
        # 1. Hardware layer selection
        if torch.cuda.is_available():
            self.device_type = "cuda"
        elif torch.backends.mps.is_available():
            self.device_type = "mps"
        else:
            self.device_type = "cpu"

        self.device = torch.device(self.device_type)
        self.tile_size = tile_size
        self.model_path = Path(f"{model_name}.pth")

        logger.info(f"Initializing Engine. Detected Hardware Layer: {self.device_type.upper()}")

        # 2. Build the neural network architecture blueprint
        if model_name == "RealESRGAN_x4plus":
            self.model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=4)
        else:
            logger.error(f"Unsupported model blueprint: {model_name}")
            raise ValueError(f"Unsupported model blueprint: {model_name}")

        # Ensure the model weight parameters are locally present
        self._ensure_weights_exist()

        # Real-ESRGAN requires a absolute string representation of the model path
        model_str_path = str(self.model_path.resolve())
        is_gpu = self.device_type in ["cuda", "mps"]

        # 3. Initialize the operational pipeline wrapper
        self.upsampler = RealESRGANer(
            scale=4,
            model_path=model_str_path,
            model=self.model,
            tile=self.tile_size if is_gpu else 0,  # Tiling protects VRAM from hitting Out-Of-Memory limits
            tile_pad=10,
            pre_pad=0,
            half=(self.device_type == "cuda")  # Enables fast FP16 execution natively on NVIDIA graphics cards
        )
        logger.info("OS-Agnostic AI Upscaler pipeline initialized and ready.")

    def _ensure_weights_exist(self):
        """Downloads model weights seamlessly to the root directory if missing."""
        if not self.model_path.exists():
            logger.warning(f"Weights missing at '{self.model_path}'. Downloading repository parameters...")
            url = f"https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/{self.model_path.name}"
            try:
                urllib.request.urlretrieve(url, self.model_path)
                logger.info("Weights downloaded successfully.")
            except Exception as e:
                logger.critical(f"Failed to fetch weights from repository: {e}")
                raise e

    def upscale_to_5k(self, input_path, output_path):
        """
        Ingests an image path, dynamically calculates the scale factor to hit
        exactly 5K width without stretching aspect ratios, and renders the output.
        """
        try:
            in_p = Path(input_path).resolve()
            out_p = Path(output_path).resolve()

            # Read image data matrix using OpenCV
            img = cv2.imread(str(in_p), cv2.IMREAD_UNCHANGED)
            if img is None:
                logger.error(f"Failed to read or decode image at: {in_p}")
                return False

            h, w = img.shape[:2]
            target_width = 5120

            # Compute exact floating-point multiplier needed to expand to 5K wide
            scale_factor = target_width / w

            logger.info(f"Processing '{in_p.name}' ({w}x{h}) -> Targets 5K via scale factor {scale_factor:.4f}")

            # Direct matrix processing to target tensor pipeline (MPS / CUDA / CPU)
            output, _ = self.upsampler.enhance(img, outscale=scale_factor)

            # Write upscaled matrix asset safely back to disk
            cv2.imwrite(str(out_p), output)
            logger.info(f"Successfully saved 5K frame to: {out_p.name}")
            return True

        except Exception as e:
            logger.exception(f"An unexpected error occurred while upscaling {input_path}: {str(e)}")
            return False