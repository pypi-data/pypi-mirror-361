# data/augmentation.py
# -- Import packages --
from PIL import Image, ImageOps, ImageEnhance, ImageFilter
import numpy as np

# -- Image augmentation for png, jpg and jpeg --
def _image_augmentation(
    img: Image.Image,
    rotation: int = 0,
    scale: float = 1.0,
    rotate_fill: tuple = (0, 0, 0),
    scale_fill: tuple = (0, 0, 0),
    flip_horizontal: bool = False,
    flip_vertical: bool = False,
    blur: int = 0,
    noise: int = 0,
    contrast: int = 0,
    brightness: int = 0,
    resize: tuple = False,
    inverse: bool = False
) -> Image.Image:
    # Make a copy to avoid modifying original
    result = img.copy()

    # 1) Rotation
    if rotation != 0:
        # PIL uses counter-clockwise for positive angles; invert for clockwise
        angle = -rotation % 360
        result = result.rotate(
            angle,
            resample=Image.BICUBIC,
            expand=True,
            fillcolor=rotate_fill
        )

    # 2) Scaling
    if scale != 1.0:
        original_size = result.size
        new_size = (int(original_size[0] * scale), int(original_size[1] * scale))
        result = result.resize(new_size, resample=Image.BICUBIC)

        # If scaling down, pad back to original size
        if scale < 1.0:
            pad_w = original_size[0] - new_size[0]
            pad_h = original_size[1] - new_size[1]
            left = pad_w // 2
            top = pad_h // 2
            right = pad_w - left
            bottom = pad_h - top
            result = ImageOps.expand(
                result,
                border=(left, top, right, bottom),
                fill=scale_fill
            )

    # 3) Horizontal flip
    if flip_horizontal:
        result = ImageOps.mirror(result)

    # 4) Vertical flip
    if flip_vertical:
        result = ImageOps.flip(result)

    # 5) Blur
    if blur and blur > 0:
        # Cap blur radius to 255
        radius = min(blur, 255)
        result = result.filter(ImageFilter.GaussianBlur(radius))

    # 6) Noise
    if noise and noise > 0:
        # Convert to numpy array
        arr = np.array(result).astype(np.int16)
        # Generate noise in range [-noise, +noise]
        noise_layer = np.random.randint(-noise, noise + 1, arr.shape, dtype=np.int16)
        noisy = arr + noise_layer
        # Clip to valid range and convert back
        noisy = np.clip(noisy, 0, 255).astype(np.uint8)
        result = Image.fromarray(noisy)

    # 7) Contrast adjustment
    if contrast != 0:
        # Map [-100..100] to [0..2], where 1 = original
        factor = (contrast + 100) / 100
        enhancer = ImageEnhance.Contrast(result)
        result = enhancer.enhance(factor)

    # 8) Brightness adjustment
    if brightness != 0:
        # Map [-100..100] to [0..2], where 1 = original
        factor = (brightness + 100) / 100
        enhancer = ImageEnhance.Brightness(result)
        result = enhancer.enhance(factor)

    # 9) Resize
    if resize and isinstance(resize, (tuple, list)) and len(resize) == 2:
        result = result.resize((int(resize[0]), int(resize[1])), resample=Image.BICUBIC)

    if inverse:
        result = ImageOps.invert(result)

    return result