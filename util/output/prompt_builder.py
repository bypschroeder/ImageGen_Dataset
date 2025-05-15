import webcolors
from collections import defaultdict


def rgba_to_color_name(rgba):
    def closest_colour(requested_colour):
        min_colours = {}
        for name in webcolors.names("css21"):
            r_c, g_c, b_c = webcolors.name_to_rgb(name)
            rd = (r_c - requested_colour[0]) ** 2
            gd = (g_c - requested_colour[1]) ** 2
            bd = (b_c - requested_colour[2]) ** 2
            min_colours[(rd + gd + bd)] = name
        return min_colours[min(min_colours.keys())]

    rgb_255 = tuple(int(x * 255) for x in rgba[:3])
    return closest_colour(rgb_255)


MATERIAL_ADJECTIVES = {
    "wood": "wooden",
    "gold": "golden",
    "silver": "silver",
    "glass": "glass",
    "plastic": "plastic",
    "metal": "metal",
    "leather": "leather",
}


def build_scene_prompt(environment, objects_metadata):
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

    return scene_data
