import blenderproc as bproc
import bpy
import numpy as np
import os
import random


def create_lighting(config, poi_obj, env_dims):
    if bpy.context.scene.world is None:
        bpy.context.scene.world = bpy.data.worlds.new("World")
    if bpy.context.scene.world.node_tree is None:
        bpy.context.scene.world.use_nodes = True

    hdri_cfg = config["lighting"]["hdri"]
    hdri_dir = os.path.abspath(hdri_cfg["path"])

    hdri_files = [
        f for f in os.listdir(hdri_dir) if f.lower().endswith((".hdr", ".exr"))
    ]
    selected_hdri = random.choice(hdri_files)

    bproc.world.set_world_background_hdr_img(
        path_to_hdr_file=os.path.join(hdri_dir, selected_hdri),
        rotation_euler=[0, 0, hdri_cfg["rotation"]],
        strength=hdri_cfg["strenght"],
    )

    light_metadata = {
        "hdri": {
            "name": selected_hdri,
            "rotation": hdri_cfg["rotation"],
            "strength": hdri_cfg["strenght"],
        }
    }

    light_cfg = config["lighting"]["light"]
    light = bproc.types.Light()
    light.set_type(light_cfg["type"])

    location_multipler = light_cfg["location_multiplier"]
    min_x = location_multipler["x"]["min"]
    max_x = location_multipler["x"]["max"]
    min_y = location_multipler["y"]["min"]
    max_y = location_multipler["y"]["max"]
    min_z = location_multipler["z"]["min"]
    max_z = location_multipler["z"]["max"]
    light_location = [
        np.random.uniform(env_dims["width"] * min_x, env_dims["width"] * max_x),
        np.random.uniform(env_dims["depth"] * min_y, env_dims["depth"] * max_y),
        np.random.uniform(env_dims["height"] * min_z, env_dims["height"] * max_z),
    ]
    light_energy = float(
        np.random.uniform(light_cfg["energy"]["min"], light_cfg["energy"]["max"])
    )

    light.set_location(light_location)
    light.set_energy(light_energy)

    if light_cfg["type"] == "AREA":
        shape = light_cfg["shape"]
        size = light_cfg["size"]
        track_axis = "TRACK_NEGATIVE_Z"
        up_axis = "UP_Y"

        light.blender_obj.data.shape = shape
        light.blender_obj.data.size = size

        constraint = light.blender_obj.constraints.new(type="TRACK_TO")
        constraint.target = poi_obj.blender_obj
        constraint.track_axis = track_axis
        constraint.up_axis = up_axis

        light_metadata["light"] = {
            "type": light_cfg["type"],
            "shape": shape,
            "size": size,
            "location": light_location,
            "energy": light_energy,
            "track_to": {
                "target_name": poi_obj.get_name(),
                "track_axis": track_axis,
                "up_axis": up_axis,
            },
        }

    return light, light_metadata
