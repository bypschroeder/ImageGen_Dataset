import blenderproc as bproc
import bpy

import argparse
import os
import random
import sys
import json


# Add necessary subdirectories to sys path for Blender
def add_subdirs_to_sys_path(root_dir):
    for dirpath, _, _ in os.walk(root_dir):
        if os.path.basename(dirpath) == "__pycache__":
            continue
        sys.path.append(dirpath)


script_dir = os.path.dirname(os.path.abspath(__file__))
add_subdirs_to_sys_path(script_dir)

from configs.config_loader import load_config
from util.mat.helper import (
    adjust_material_mapping_by_scale,
    import_mats,
)
from util.obj.mesh import create_object
from util.obj.sample_poses import generate_pose_on_table, generate_pose_under_table
from util.output.path import get_next_index
from util.output.render import save_image
from util.scene.base_scenes.simple_room import generate_simple_room
from util.scene.camera import create_camera_pose, sample_camera_location, set_intrinsics
from util.scene.light import setup_point_lights, setup_area_lights, setup_lights
from util.output.metadata_builder import build_metadata
from util.output.prompt_builder import build_scene_prompt


# Load config
cfg = load_config(os.path.abspath("./configs/room_config.json"))

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--iterations", type=int, default=1)
parser.add_argument("-o", "--output", type=str, help="The output directory")
args = parser.parse_args()

os.makedirs(args.output, exist_ok=True)

bproc.init()

# BlenderProc Settings
# bproc.renderer.enable_normals_output()
# bproc.renderer.enable_depth_output(activate_antialiasing=False)
# bproc.renderer.enable_diffuse_color_output()
bproc.renderer.set_max_amount_of_samples(cfg["render"]["samples"])
bproc.renderer.set_denoiser("OPTIX")
bpy.context.scene.eevee.use_raytracing = True


for i in range(args.iterations):
    # Path
    next_index_str = get_next_index(args.output)

    # Materials
    floor_mats = import_mats(os.path.abspath(cfg["materials"]["env"]["floor"]))
    wall_mats = import_mats(os.path.abspath(cfg["materials"]["env"]["wall"]))
    table_mats = import_mats(os.path.abspath(cfg["materials"]["env"]["table"]))
    obj_mats = import_mats(os.path.abspath(cfg["materials"]["objects"]))

    tabletop_mats = [
        mat for mat in table_mats if mat and mat.get_name().startswith("Tabletop")
    ]
    tableleg_mats = [
        mat for mat in table_mats if mat and mat.get_name().startswith("Tableleg")
    ]

    # Config
    ENV_DIMS = {
        "width": random.randint(
            cfg["room"]["width"]["min"], cfg["room"]["width"]["max"]
        ),
        "depth": random.randint(
            cfg["room"]["depth"]["min"], cfg["room"]["depth"]["max"]
        ),
        "height": cfg["room"]["height"],
    }
    FLOOR_MAT = random.choice(floor_mats)
    WALL_MAT = random.choice(wall_mats)
    TABLETOP_MAT = random.choice(tabletop_mats)
    TABLELEG_MAT = random.choice(tableleg_mats)

    # Setup Base Scene
    floor, walls = generate_simple_room(ENV_DIMS, room_offset_y=-1)
    floor.enable_rigidbody(active=False, collision_shape="BOX")

    table = bproc.loader.load_blend("./assets/objects/table.blend")[0]
    if isinstance(table, bproc.types.MeshObject):
        table.enable_rigidbody(active=False, collision_shape="MESH")

    # Materials
    if FLOOR_MAT:
        floor.add_material(FLOOR_MAT)
    adjust_material_mapping_by_scale(floor)
    if WALL_MAT:
        for wall in walls:
            wall.add_material(WALL_MAT)
            adjust_material_mapping_by_scale(wall)
    if TABLELEG_MAT:
        if isinstance(table, bproc.types.MeshObject):
            table.set_material(index=0, material=TABLELEG_MAT)
    if TABLETOP_MAT:
        if isinstance(table, bproc.types.MeshObject):
            table.set_material(index=1, material=TABLETOP_MAT)

    # Create Objects
    objects_on_table = []
    objects_under_table = []

    objects_metadata = []
    for j in range(
        random.randint(cfg["objects"]["min_objects"], cfg["objects"]["max_objects"])
    ):
        SHAPE = random.choice(["CUBE", "CYLINDER", "CONE", "SPHERE"])
        MAT = random.choice(obj_mats)
        SIZE_NAME, SIZE_VALUE = random.choice(
            list(cfg["objects"]["size_options"].items())
        )

        obj = create_object(scale=SIZE_VALUE, shading_mode="smooth", shape=SHAPE)

        if MAT:
            obj.add_material(MAT)

        on_table = random.random() < cfg["objects"]["location_rate"]

        objects_metadata.append(
            {
                "shape": SHAPE,
                "size": {
                    "name": SIZE_NAME,
                    "value": SIZE_VALUE,
                },
                "material": MAT.get_name().split(".")[0] if MAT else "no material",
                "position": {
                    "name": "on table" if on_table else "under table",
                    "coordinates": None,
                },
            }
        )

        if on_table:
            objects_on_table.append(obj)
        else:
            objects_under_table.append(obj)

    # Pose Objects
    if objects_on_table:
        generate_pose_on_table(table, objects_on_table, margin=0.2)

    if objects_under_table:
        generate_pose_under_table(table, floor, objects_under_table, margin=0.2)

    all_objects = objects_on_table + objects_under_table

    for obj in all_objects:
        obj.enable_rigidbody(True)

    bproc.object.simulate_physics_and_fix_final_poses(
        min_simulation_time=2, max_simulation_time=4, check_object_interval=1
    )

    for obj_metadata, obj in zip(objects_metadata, all_objects):
        coordinates = obj.get_location()
        obj_metadata["position"]["coordinates"] = coordinates.tolist()

    # Camera
    set_intrinsics(
        cfg["render"]["resolution_x"],
        cfg["render"]["resolution_y"],
        cfg["camera"]["focal_length"],
    )

    poi = bproc.object.compute_poi([table] + all_objects)

    for _ in range(cfg["camera"]["num_poses"]):
        location = sample_camera_location(
            cfg["camera"]["location"]["min"], cfg["camera"]["location"]["max"]
        )
        cam2world = create_camera_pose(poi, location)
        bproc.camera.add_camera_pose(cam2world)

    camera_metadata = {
        "resolution": {
            "x": cfg["render"]["resolution_x"],
            "y": cfg["render"]["resolution_y"],
        },
        "focal_length": cfg["camera"]["focal_length"],
        "point_of_interest": poi.tolist(),
        "camera_locations": [
            bproc.camera.get_camera_pose(i)[:3, 3].tolist()
            for i in range(cfg["camera"]["num_poses"])
        ],
    }

    # Light
    lights, light_metadata = setup_lights(ENV_DIMS, table, cfg)

    # Render
    output_path = args.output

    data = bproc.renderer.render()
    save_image(data["colors"], output_path, next_index_str)

    # Save Metadata
    metadata = build_metadata(
        "room",
        ENV_DIMS,
        floor,
        walls,
        table,
        camera_metadata,
        light_metadata,
        objects_metadata,
    )
    with open(
        os.path.join(output_path, f"{next_index_str}_metadata.json"),
        "w",
    ) as f:
        json.dump(metadata, f, indent=4)

    # Save Prompt
    prompt_data = build_scene_prompt(
        environment="room", objects_metadata=objects_metadata
    )
    with open(os.path.join(output_path, f"{next_index_str}_prompt.json"), "w") as f:
        json.dump(prompt_data, f, indent=4)

    bproc.clean_up(clean_up_camera=True)
