import blenderproc as bproc
import os
import sys
import argparse
import random
import json
import numpy as np


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
    import_mats,
    adjust_material_mapping_by_scale,
)
from util.output.path import get_next_index
from util.scene.base_scenes.simple_room import generate_simple_room
from util.scene.camera import create_camera_pose, set_intrinsics, sample_camera_location
from util.obj.mesh import create_object
from util.output.render import (
    prepare_output_dirs,
    render_and_save_hdf5,
    extract_images_from_hdf5,
)
from util.obj.sample_poses import generate_pose_on_table, generate_pose_under_table
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
bproc.renderer.set_max_amount_of_samples(cfg.render.samples)


for i in range(args.iterations):
    # Path
    next_index_str = get_next_index(args.output)

    # Materials
    floor_mats = import_mats(os.path.abspath(cfg.materials.env.floor))
    wall_mats = import_mats(os.path.abspath(cfg.materials.env.wall))
    table_mats = import_mats(os.path.abspath(cfg.materials.env.table))
    obj_mats = import_mats(os.path.abspath(cfg.materials.objects))

    # Config
    ENV_DIMS = {
        "width": random.randint(cfg.room.width.min, cfg.room.width.max),
        "depth": random.randint(cfg.room.depth.min, cfg.room.depth.max),
        "height": cfg.room.height,
    }
    FLOOR_MAT = random.choice(floor_mats)
    WALL_MAT = random.choice(wall_mats)
    TABLE_MAT = random.choice(table_mats)

    # Setup Base Scene
    floor, ceiling, walls = generate_simple_room(ENV_DIMS)
    floor.enable_rigidbody(active=False, collision_shape="BOX")

    table = bproc.loader.load_blend("./assets/objects/table.blend")[0]
    table.enable_rigidbody(active=False, collision_shape="MESH")

    # Materials
    floor.add_material(FLOOR_MAT)
    adjust_material_mapping_by_scale(floor)
    for wall in walls:
        wall.add_material(WALL_MAT)
        adjust_material_mapping_by_scale(wall)
    table.set_material(index=1, material=TABLE_MAT)

    # Create Objects
    objects_on_table = []
    objects_under_table = []

    for j in range(random.randint(1, 2)):
        SHAPE = random.choice(["CUBE", "CYLINDER", "CONE"])
        MAT = random.choice(obj_mats)
        SIZE_OPTIONS = vars(cfg.objects.size_options)
        SIZE_NAME, SIZE_VALUE = random.choice(list(SIZE_OPTIONS.items()))

        obj = create_object(scale=SIZE_VALUE, shading_mode="smooth", shape=SHAPE)

        obj.add_material(MAT)

        on_table = random.random() < cfg.objects.location_rate

        if on_table:
            objects_on_table.append(obj)
        else:
            objects_under_table.append(obj)

    # Pose Objects
    if objects_on_table:
        generate_pose_on_table(table, objects_on_table)

    if objects_under_table:
        generate_pose_under_table(table, floor, objects_under_table)

    all_objects = objects_on_table + objects_under_table

    for obj in all_objects:
        obj.enable_rigidbody(True)
    # floor.enable_rigidbody(False)

    bproc.object.simulate_physics_and_fix_final_poses(
        min_simulation_time=2, max_simulation_time=4, check_object_interval=1
    )

    # Camera
    set_intrinsics(
        cfg.render.resolution_x, cfg.render.resolution_y, cfg.camera.focal_length
    )

    poi = bproc.object.compute_poi([table] + all_objects)

    for _ in range(cfg.camera.num_poses):
        location = sample_camera_location(
            cfg.camera.location.min, cfg.camera.location.max
        )
        cam2world = create_camera_pose(poi, location)
        bproc.camera.add_camera_pose(cam2world)

    # Light
    # light = sample_point_light(poi)
    bproc.lighting.light_surface(
        [ceiling],
        emission_strength=np.random.uniform(
            cfg.light.light_surface.strength.min, cfg.light.light_surface.strength.max
        ),
        emission_color=cfg.light.light_surface.color,
    )

    # Render
    output_path = os.path.join(args.output, next_index_str)
    dirs = prepare_output_dirs(output_path)

    if cfg.output.hdf5:
        data = render_and_save_hdf5(dirs["hdf5"])

    if cfg.output.convert_to_png:
        extract_images_from_hdf5(dirs["hdf5"], dirs)

    # Save Metadata
    # metadata = build_metadata(
    #     floor, walls, table, objects_on_table, objects_under_table, ENV_DIMS
    # )
    # with open(
    #     os.path.join(output_path, "metadata.json"),
    #     "w",
    # ) as f:
    #     json.dump(metadata, f, indent=4)

    # # Save Prompt
    # prompt_data = build_scene_prompt(metadata)
    # with open(os.path.join(output_path, "prompt.json"), "w") as f:
    #     json.dump(prompt_data, f, indent=4)

    bproc.clean_up(clean_up_camera=True)
