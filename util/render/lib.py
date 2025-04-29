import numpy as np


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
