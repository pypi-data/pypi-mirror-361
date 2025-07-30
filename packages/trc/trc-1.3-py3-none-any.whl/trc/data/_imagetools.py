# data/imagetools.py
# -- Import packages --
from PIL import Image, ImageFilter
import numpy as np

# -- Image similarity --
def _image_similarity(img1: Image.Image,
                     img2: Image.Image,
                     pixel: bool = True,
                     shape: bool = True,
                     color: bool = True,
                     resize_mode=None) -> float:
    # 1) Resize images
    w1, h1 = img1.size
    w2, h2 = img2.size
    try:
        rm = float(resize_mode)
    except Exception:
        rm = None
    if rm == 1.0:
        target = (w1, h1)
    elif rm == 2.0:
        target = (w2, h2)
    else:
        target = (int(round((w1 + w2) / 2)), int(round((h1 + h2) / 2)))
    img1 = img1.resize(target, Image.BILINEAR)
    img2 = img2.resize(target, Image.BILINEAR)

    # Convert to RGBA for pixel and color modes
    img1_rgba = img1.convert("RGBA")
    img2_rgba = img2.convert("RGBA")

    scores = []

    # 2) Pixel mode
    if pixel:
        a1 = np.asarray(img1_rgba, dtype=np.float32)
        a2 = np.asarray(img2_rgba, dtype=np.float32)
        diff = np.abs(a1 - a2) / 255.0
        scores.append(np.clip(1.0 - diff.mean(), 0.0, 1.0))

    # 3) Shape mode using Hausdorff-like distance on edges
    if shape:
        # Edge detection
        e1 = img1.convert("L").filter(ImageFilter.FIND_EDGES)
        e2 = img2.convert("L").filter(ImageFilter.FIND_EDGES)
        # Binarize edges via adaptive threshold
        arr1 = np.asarray(e1, dtype=np.float32) / 255.0
        arr2 = np.asarray(e2, dtype=np.float32) / 255.0
        thr1 = arr1.mean() + arr1.std()
        thr2 = arr2.mean() + arr2.std()
        b1 = np.argwhere(arr1 > thr1)
        b2 = np.argwhere(arr2 > thr2)
        if b1.size == 0 or b2.size == 0:
            scores.append(0.0)
        else:
            # directed Hausdorff distances
            def directed_hausdorff(A, B):
                dists = np.sqrt(((A[:, None, :] - B[None, :, :]) ** 2).sum(axis=2))
                return dists.min(axis=1).max()
            d1 = directed_hausdorff(b1, b2)
            d2 = directed_hausdorff(b2, b1)
            dh = max(d1, d2)
            # normalize by image diagonal
            diag = np.sqrt(target[0]**2 + target[1]**2)
            sim = 1.0 - dh/diag
            scores.append(np.clip(sim, 0.0, 1.0))

    # 4) Color mode
    if color:
        nx = max(1, target[0] // 64)
        ny = max(1, target[1] // 64)
        w_reg = target[0] // nx
        h_reg = target[1] // ny
        def avg_colors(img):
            arr = np.asarray(img.convert("RGBA"), dtype=np.float32)
            regs = []
            for i in range(ny):
                for j in range(nx):
                    block = arr[i*h_reg:(i+1)*h_reg, j*w_reg:(j+1)*w_reg]
                    if block.size:
                        regs.append(block.mean(axis=(0,1)))
            return np.array(regs)
        c1, c2 = avg_colors(img1), avg_colors(img2)
        m = min(len(c1), len(c2))
        if m == 0:
            scores.append(0.0)
        else:
            diff = np.abs(c1[:m] - c2[:m]) / 255.0
            scores.append(np.clip(1.0 - diff.mean(), 0.0, 1.0))

    # 5) Combine scores
    return float(np.mean(scores)) if scores else 0.0

# -- Image blending --
def _blend_images(*images) -> Image.Image:
    # Flatten inputs and filter valid image types
    def flatten_and_filter(items):
        for item in items:
            if isinstance(item, (list, tuple)) and not isinstance(item, (Image.Image, np.ndarray)):
                yield from flatten_and_filter(item)
            elif isinstance(item, (Image.Image, np.ndarray)):
                yield item
            # else: ignore non-image

    imgs = list(flatten_and_filter(images))
    if not imgs:
        raise ValueError("Need at least one valid image or array to blend")

    # Convert all to numpy arrays
    np_imgs = []
    for img in imgs:
        if isinstance(img, Image.Image):
            arr = np.asarray(img, dtype=np.float32)
        else:  # numpy array
            arr = img.astype(np.float32)
        np_imgs.append(arr)

    # Ensure same shape and three or four channels
    shapes = {arr.shape for arr in np_imgs}
    if len(shapes) > 1:
        raise ValueError("All images/arrays must have the same shape")

    # Compute average
    stacked = np.stack(np_imgs, axis=0)
    mean_arr = np.mean(stacked, axis=0)
    mean_arr = np.clip(mean_arr, 0, 255).astype(np.uint8)

    # Convert back to PIL, infer mode from array shape
    channels = mean_arr.shape[2] if mean_arr.ndim == 3 else 1
    if channels == 1:
        mode = 'L'
    elif channels == 3:
        mode = 'RGB'
    elif channels == 4:
        mode = 'RGBA'
    else:
        raise ValueError(f"Unsupported number of channels: {channels}")

    return Image.fromarray(mean_arr, mode)