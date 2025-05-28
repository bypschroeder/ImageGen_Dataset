import blenderproc as bproc
import numpy as np
import os
from PIL import Image

from utils.general.path import get_next_index


def save_image(data, out_dir, next_index_str, normalize_fn=None):
    for idx, img in enumerate(data):
        array = np.squeeze(np.array(img))

        if normalize_fn:
            array = normalize_fn(array)
        elif array.dtype != np.uint8:
            array = (array * 255).clip(0, 255).astype(np.uint8)

        image = Image.fromarray(array)
        image.save(os.path.join(out_dir, f"{next_index_str}_{idx:01d}.png"))


def render(output_dir):
    data = bproc.renderer.render()

    next_index_str = get_next_index(output_dir)
    save_image(data["colors"], output_dir, next_index_str)
