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


def prepare_output_dirs(base_path):
    paths = {
        "hdf5": os.path.join(base_path, "hdf5"),
        "colors": os.path.join(base_path, "colors"),
        # "depth": os.path.join(base_path, "depth"),
        # "normals": os.path.join(base_path, "normals"),
        # "diffuse": os.path.join(base_path, "diffuse"),
    }
    for path in paths.values():
        os.makedirs(path, exist_ok=True)
    return paths


def render_and_save_hdf5(hdf5_output_path):
    data = bproc.renderer.render()
    bproc.writer.write_hdf5(hdf5_output_path, data)
    return data


def extract_images_from_hdf5(hdf5_dir, output_dirs):
    for file_name in os.listdir(hdf5_dir):
        if not file_name.endswith(".hdf5"):
            continue

        path = os.path.join(hdf5_dir, file_name)

        with h5py.File(path, "r") as f:
            if "colors" in f:
                save_image(f["colors"], output_dirs["colors"], file_name)

            if "depth" in f:
                save_image(f["depth"], output_dirs["depth"], file_name, normalize_depth)

            if "normals" in f:
                save_image(
                    f["normals"], output_dirs["normals"], file_name, normalize_normals
                )

            if "diffuse" in f:
                save_image(
                    f["diffuse"], output_dirs["diffuse"], file_name, normalize_diffuse
                )


def save_image(data, out_dir, file_name, normalize_fn=None):
    array = np.array(data)
    if normalize_fn:
        array = normalize_fn(array)
    elif array.dtype != np.uint8:
        array = (array * 255).clip(0, 255).astype(np.uint8)

    img = Image.fromarray(array)
    img.save(os.path.join(out_dir, file_name.replace(".hdf5", ".png")))
