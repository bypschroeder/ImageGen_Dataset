import os
import json

from collections import defaultdict
from utils.general.path import get_next_index


MATERIAL_ADJECTIVES = {
    "wood": "wooden",
    "gold": "golden",
    "silver": "silver",
    "glass": "glass",
    "plastic": "plastic",
    "metal": "metal",
    "leather": "leather",
}


def save_prompt(environment, objects_metadata, output_dir):
    scene_data = {"prompt": "", "objects": []}
    position_groups = defaultdict(list)

    for metadata in objects_metadata:
        shape = metadata["shape"].lower()
        size = metadata["size"]["name"]
        material = metadata["material"].lower()

        position_name = metadata["position"]["name"]
        pos_parts = position_name.split(" ", 1)
        local_preposition = pos_parts[0]
        base = pos_parts[1] if len(pos_parts) > 1 else "surface"

        obj_description = {
            "shape": shape,
            "size": size,
            "material": material,
            "local_preposition": local_preposition,
            "base": base,
        }

        scene_data["objects"].append(obj_description)
        position_groups[position_name].append(obj_description)

    object_phrases = []
    for position, descriptions in position_groups.items():
        preposition = descriptions[0]["local_preposition"]
        base = descriptions[0]["base"]
        material_adj = MATERIAL_ADJECTIVES.get(
            descriptions[0]["material"], descriptions[0]["material"]
        )

        if len(descriptions) == 1:
            d = descriptions[0]
            phrase = f"a {d['size']} {material_adj} {d['shape']} is placed {preposition} the {base}"
        else:
            joined = ", ".join(
                [
                    f"a {d['size']} {material_adj} {d['shape']}"
                    for d in descriptions[:-1]
                ]
            )
            joined += f" and a {descriptions[-1]['size']} {descriptions[-1]['material']} {descriptions[-1]['shape']}"
            phrase = f"{joined} are placed {preposition} the {base}"

        object_phrases.append(phrase)

    scene_data["prompt"] = (
        f"In a simple {environment}, " + " and ".join(object_phrases) + "."
    )

    next_index_str = get_next_index(output_dir)

    with open(os.path.join(output_dir, f"{next_index_str}_prompt.json"), "w") as f:
        json.dump(scene_data, f, indent=4)

    return scene_data
