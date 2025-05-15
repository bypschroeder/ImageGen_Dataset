import os
import h5py
import numpy as np
from PIL import Image
import blenderproc as bproc


def normalize_depth(depth):
    depth_min = np.min(depth)
    depth_max = np.max(depth)
    if depth_max - depth_min == 0:
        return np.zeros_like(depth, dtype=np.uint8)
    depth_norm = (depth - depth_min) / (depth_max - depth_min)
    return (depth_norm * 255).astype(np.uint8)


def normalize_normals(normals):
    normals = ((normals + 1.0) / 2.0 * 255.0).clip(0, 255).astype(np.uint8)
    return normals


def normalize_diffuse(diffuse):
    diffuse = (diffuse.clip(0.0, 1.0) * 255.0).astype(np.uint8)
    return diffuse


def save_image(data, out_dir, normalize_fn=None):
    for idx, img in enumerate(data):
        array = np.squeeze(np.array(img))

        if normalize_fn:
            array = normalize_fn(array)
        elif array.dtype != np.uint8:
            array = (array * 255).clip(0, 255).astype(np.uint8)

        image = Image.fromarray(array)
        image.save(os.path.join(out_dir, f"{idx:01d}.png"))
