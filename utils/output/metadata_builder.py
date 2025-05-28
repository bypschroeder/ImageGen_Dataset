import os
import json

from utils.general.path import get_next_index


def save_metadata(
    environment, env_dims, floor, walls, table, camera, light, objects, output_dir
):
    metadata = {
        "environment": environment,
        "env_dimensions": env_dims,
        "env_materials": {
            "floor_material": floor.get_materials()[0].get_name().split(".")[0],
            "wall_material": walls[0].get_materials()[0].get_name().split(".")[0],
            "table_material": table.get_materials()[1].get_name().split(".")[0],
        },
        "camera": camera,
        "lighting": light,
        "objects": objects,
    }

    next_index_str = get_next_index(output_dir)

    with open(
        os.path.join(output_dir, f"{next_index_str}_metadata.json"),
        "w",
    ) as f:
        json.dump(metadata, f, indent=4)

    return metadata
