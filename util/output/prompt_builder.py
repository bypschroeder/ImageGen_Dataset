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


def build_scene_prompt(metadata):
    scene_data = {"prompt": "", "objects": []}

    position_groups = defaultdict(list)

    for obj in metadata.get("objects", []):
        color = rgba_to_color_name(obj["material"]["base_color"])
        shape = obj["name"].lower()
        position = obj.get("position", "somewhere")

        scene_data["objects"].append(
            {"name": shape, "color": color, "position": position}
        )

        position_groups[position].append(f"a {color} {shape}")

    object_phrases = []
    for position, descriptions in position_groups.items():
        position_parts = position.split(" ")
        if len(descriptions) == 1:
            object_phrases.append(
                f"{descriptions[0]} is placed {position_parts[0]} a {position_parts[1]}"
            )
        else:
            joined = " and ".join(descriptions)
            object_phrases.append(
                f"{joined} are placed {position_parts[0]} a {position_parts[1]}"
            )

    scene_data["prompt"] = "In a simple room " + " and ".join(object_phrases) + "."

    return scene_data
