
from pathlib import Path
from typing import Optional, Union

import numpy as np
from PIL import Image
from scipy.ndimage import convolve1d

try:
    from rich.console import Console
    console = Console()
except ImportError:
    console = None

# Default 5-tap kernel (HALO tap, two-phase optimized)
DEFAULT_5TAP_KERNEL = [
    -0.21982911229133606,
    0.15102669596672058,
    0.29002970457077026,
    0.6013770699501038,
    0.17739564180374146
]

def upscale(
    input_data: Union[str, Path, np.ndarray],
    scale: int,
    save_path: Optional[Union[str, Path]] = None,
    boundary: str = 'reflect',
    verbose: bool = False
) -> Union[str, Image.Image]:
    """
    Upscale an image by an integer scale factor using a separable 5-tap kernel (no subpixel adaptation), preserving color and ICC profile.

    Args:
        input_data: Path to the input image (str or Path), or a NumPy array.
        scale: Integer upscaling factor >= 1. Only integer scales are supported.
        save_path: Path to save the upscaled image. If None, generates a path like <input>_2x.<ext>.
        boundary: Convolution boundary mode (e.g. 'reflect', 'nearest'). Default is 'reflect' for smooth borders.
        verbose: Ignored (kept for API compatibility).

    Returns:
        str: The path where the upscaled image was saved (if input is a file path).
        Image.Image: The upscaled PIL Image (if input is a NumPy array).

    Raises:
        ValueError: If scale is not a positive integer.
        OSError: If saving the image fails.
    """
    if not (isinstance(scale, int) and scale >= 1):
        raise ValueError("scale must be a positive integer (>=1)")
    kernel = np.array(DEFAULT_5TAP_KERNEL, dtype=np.float32)
    kernel /= kernel.sum()

    if isinstance(input_data, (str, Path)):
        with Image.open(input_data) as img:
            icc_profile = img.info.get('icc_profile')
            if save_path is None:
                p = Path(input_data)
                scale_str = f"{scale}x"
                save_path = str(p.with_name(f"{p.stem}_{scale_str}{p.suffix}"))
            else:
                save_path = Path(save_path)

            if Path(save_path).exists():
                raise FileExistsError(f"Output file already exists: {save_path}")

            is_jpeg = str(save_path).lower().endswith(('.jpg', '.jpeg'))
            if is_jpeg:
                if img.mode != "RGB":
                    img = img.convert("RGB")
            else:
                if img.mode not in ("RGB", "RGBA"):
                    img = img.convert("RGBA" if "A" in img.getbands() else "RGB")
            arr = np.array(img).astype(np.float32)
            if arr.ndim == 2:
                arr = arr[..., None]
            arr_up = arr.repeat(scale, axis=0).repeat(scale, axis=1)
            arr_up = convolve1d(arr_up, kernel, axis=1, mode=boundary)
            arr_up = convolve1d(arr_up, kernel, axis=0, mode=boundary)
            arr_up = np.clip(arr_up, 0, 255).astype(np.uint8)
            if arr_up.shape[2] == 1:
                arr_up = arr_up[..., 0]
            out_img = Image.fromarray(arr_up, mode=img.mode if arr_up.ndim == 2 else ("RGB" if arr_up.shape[2] == 3 else "RGBA"))
            save_kwargs = {}
            if icc_profile:
                save_kwargs['icc_profile'] = icc_profile
            if is_jpeg:
                save_kwargs['quality'] = 95
                save_kwargs['subsampling'] = 0
                if out_img.mode != "RGB":
                    out_img = out_img.convert("RGB")
            try:
                out_img.save(save_path, **save_kwargs)
            except Exception as e:
                raise OSError(f"Failed to save image to {save_path}: {e}") from e
        return str(save_path)
    elif isinstance(input_data, np.ndarray):
        arr = input_data.astype(np.float32)
        orig_mode = None
        if arr.ndim == 2:
            arr = arr[..., None]
            orig_mode = "L"
        elif arr.ndim == 3:
            if arr.shape[2] == 1:
                orig_mode = "L"
            elif arr.shape[2] == 3:
                orig_mode = "RGB"
            elif arr.shape[2] == 4:
                orig_mode = "RGBA"
            else:
                raise ValueError("Unsupported channel count in input array.")
        else:
            raise ValueError("Input array must be 2D or 3D (HWC format).")
        arr_up = arr.repeat(scale, axis=0).repeat(scale, axis=1)
        arr_up = convolve1d(arr_up, kernel, axis=1, mode=boundary)
        arr_up = convolve1d(arr_up, kernel, axis=0, mode=boundary)
        arr_up = np.clip(arr_up, 0, 255).astype(np.uint8)
        if arr_up.shape[2] == 1:
            arr_up = arr_up[..., 0]
        out_img = Image.fromarray(arr_up, mode=orig_mode if arr_up.ndim == 2 else ("RGB" if arr_up.shape[2] == 3 else "RGBA"))
        return out_img
    else:
        raise TypeError("input_data must be a file path, Path, or a NumPy array.")
