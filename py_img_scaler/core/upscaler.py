import os
import cv2
import collections.namedtuple
import torch
import torch.nn as nn
import logging
import urllib.request
import numpy as np
from pathlib import Path
from torchsr.models import ninasr_b0  # Example native super-res model

# Retrieve the pre-configured global application logger
logger = logging.getLogger("PyImgScaler")

# Quick and Dirty, but effective, check for GPU availability and type
# TODO: Refactor for more robust error handling and support
# TODO: Refactor Upscaler configuration to its own class or config file for better maintainability and testability
class AIUpscaler:
    def __init__(self, model_name="ninasr_b0", tile_size=400):
        """
        Cross-platform AI engine supporting NVIDIA CUDA, AMD ROCm (Linux), MPS (macOS), and CPU fallback.
        Powered by torchsr natively.
        """
        # 1. Hardware layer selection
        if torch.cuda.is_available():
            self.device_type = "cuda"
            if hasattr(torch.version, "hip") and torch.version.hip is not None:
                self.hardware_vendor = "AMD ROCm"
            else:
                self.hardware_vendor = "NVIDIA CUDA"
        elif torch.backends.mps.is_available():
            self.device_type = "mps"
            self.hardware_vendor = "APPLE MPS"
        else:
            self.device_type = "cpu"
            self.hardware_vendor = "CPU FALLBACK"

        self.device = torch.device(self.device_type)
        self.tile_size = tile_size

        logger.info(f"Initializing Engine. Hardware Layer: {self.hardware_vendor}; Device Type: {self.device_type}")

        # 2. Build the model natively from torchsr
        # Note: torchsr natively ships models like NinaSR, EDSR, and RCAN.
        if model_name == "ninasr_b0":
            # NinaSR b0 has a default scale factor of 4x built into its architecture
            self.model = ninasr_b0(scale=4, pretrained=True)
        else:
            logger.error(f"Unsupported torchsr model blueprint: {model_name}")
            raise ValueError(f"Unsupported torchsr model blueprint: {model_name}")

        self.model.to(self.device)
        self.model.eval()

        # Enable FP16 native execution for discrete GPUs (CUDA/ROCm) to optimize VRAM/speed
        self.use_fp16 = self.device_type == "cuda"
        if self.use_fp16:
            self.model.half()

        logger.info("torchsr AI Upscaler pipeline initialized and ready.")

    # TODO: unoptimized, but functional, tiling implementation for large images to avoid VRAM allocation crashes
    def _process_tensor(self, img_np):
        """Converts an OpenCV BGR image into a normalized PyTorch tensor ready for ML execution."""
        # Convert BGR to RGB, normalize to [0, 1], shape to [C, H, W]
        img_rgb = cv2.cvtColor(img_np, cv2.COLOR_BGR2RGB)
        img_tensor = torch.from_numpy(img_rgb).permute(2, 0, 1).float() / 255.0
        img_tensor = img_tensor.unsqueeze(0).to(self.device)  # Add batch dimension [1, C, H, W]

        if self.use_fp16:
            img_tensor = img_tensor.half()
        return img_tensor

    # TODO: unoptimized, but functional, post-processing implementation for converting tensors back to OpenCV images
    def _postprocess_tensor(self, tensor):
        """Converts a normalized PyTorch output tensor back into a standard OpenCV image matrix."""
        tensor = tensor.squeeze(0).clamp(0, 1).permute(1, 2, 0)
        img_rgb = (tensor.cpu().numpy() * 255.0).astype(np.uint8)
        return cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

    def _enhance_with_tiling(self, img_tensor):
        """
        Processes large images by splitting them into tiles to prevent VRAM allocation crashes.
        """
        batch, channels, height, width = img_tensor.shape
        scale = 4  # Matches ninasr_b0 native output footprint

        output_h, output_w = height * scale, width * scale
        output_tensor = torch.zeros((batch, channels, output_h, output_w), dtype=img_tensor.dtype, device=self.device)

        pad = 12  # Padding limits seam artifacts between adjoining processing blocks

        for y in range(0, height, self.tile_size):
            for x in range(0, width, self.tile_size):
                # Calculate bounds for slicing with padding safeguards
                y0, y1 = max(y - pad, 0), min(y + self.tile_size + pad, height)
                x0, x1 = max(x - pad, 0), min(x + self.tile_size + pad, width)

                tile = img_tensor[:, :, y0:y1, x0:x1]

                with torch.no_grad():
                    tile_output = self.model(tile)

                # Trim padding out from the output matrix slice calculations
                out_y0 = (y - y0) * scale
                out_y1 = out_y0 + (min(y + self.tile_size, height) - y) * scale
                out_x0 = (x - x0) * scale
                out_x1 = out_x0 + (min(x + self.tile_size, width) - x) * scale

                target_y0, target_y1 = y * scale, min(y + self.tile_size, height) * scale
                target_x0, target_x1 = x * scale, min(x + self.tile_size, width) * scale

                output_tensor[:, :, target_y0:target_y1, target_x0:target_x1] = tile_output[:, :, out_y0:out_y1, out_x0:out_x1]

        return output_tensor

    # TODO: Add support for batch processing of multiple images in a single call to improve throughput, if possible
    # TODO: Add support for custom output resolutions. Im just hardcoding 5K because thats my personal use case. But this should be a user-configurable option.
    def upscale_to_5k(self, input_path, output_path):
        """
        Ingests an image path, runs it through the neural network pipeline, and
        uses an accurate bicubic interpolation resize to hit exactly 5K width.
        """
        try:
            in_p = Path(input_path).resolve()
            out_p = Path(output_path).resolve()

            img = cv2.imread(str(in_p), cv2.IMREAD_UNCHANGED)
            if img is None:
                logger.error(f"Failed to read or decode image at: {in_p}")
                return False

            h, w = img.shape[:2]
            # TODO: Ensure that the input image is not smaller than the target resolution to avoid upscaling artifacts
            # TODO: Add support for aspect ratio preservation and letterboxing/pillarboxing if the input image is not 21:9
            # TODO: Make configurable for different target resolutions, not just 5K, and allow user-defined scaling factors
            target_width = 5120
            target_height = 2160 # 5k2k cuz that what I use...
            scale_factor = target_width / w

            logger.info(f"Processing '{in_p.name}' ({w}x{h}) -> Targets 5K via model + target scaling")

            # 1. Image preprocessing to clean PyTorch tensor
            img_tensor = self._process_tensor(img)

            # 2. Network enhancement execution (with VRAM protection tiling if on GPU)
            if self.device_type in ["cuda", "mps"]:
                enhanced_tensor = self._enhance_with_tiling(img_tensor)
            else:
                with torch.no_grad():
                    enhanced_tensor = self.model(img_tensor)

            # 3. Bring the generated high-res canvas back to Numpy/OpenCV
            upscaled_img = self._postprocess_tensor(enhanced_tensor)

            # 4. Bring the output to exactly 5K wide if the network's 4x scale doesn't perfectly match
            final_h = int(h * scale_factor)
            if upscaled_img.shape[1] != target_width:
                upscaled_img = cv2.resize(upscaled_img, (target_width, final_h), interpolation=cv2.INTER_CUBIC)

            # Save frame back to physical media disk asset
            cv2.imwrite(str(out_p), upscaled_img)
            logger.info(f"Successfully {target_width}x{target_height} to frame to: {out_p.name}")
            return True

        except Exception as e:
            logger.exception(f"An unexpected error occurred while upscaling {input_path}: {str(e)}")
            return False
