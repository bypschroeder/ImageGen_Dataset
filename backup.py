import blenderproc as bproc
import os
import sys
import argparse
import random
import numpy as np
import json


# Add necessary subdirectories to sys path for Blender
def add_subdirs_to_sys_path(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if os.path.basename(dirpath) == "__pycache__":
            continue
        sys.path.append(dirpath)


script_dir = os.path.dirname(os.path.abspath(__file__))
add_subdirs_to_sys_path(script_dir)

from util.output.path import get_next_index
from util.scene.base_scenes.simple_room import generate_simple_room
from util.scene.light import sample_light
from util.scene.camera import create_camera_pose, set_intrinsics, sample_camera_location
from util.obj.mesh import create_object
from util.mat.base import (
    create_environment_materials,
    generate_distinct_rgba,
    create_material_for_color,
)
from util.output.render import (
    prepare_output_dirs,
    render_and_save_hdf5,
    extract_images_from_hdf5,
)
from util.obj.sample_poses import generate_pose_on_table, generate_pose_under_table
from util.output.metadata_builder import build_metadata
from util.output.prompt_builder import build_scene_prompt

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
bproc.renderer.set_max_amount_of_samples(128)


for i in range(args.iterations):
    # Path
    next_index_str = get_next_index(args.output)

    # Config
    env_dims = {
        "width": random.randint(5, 15),
        "depth": random.randint(5, 15),
        "height": 6,
    }

    # Base environment
    floor, walls = generate_simple_room(
        width=env_dims["width"], depth=env_dims["depth"], height=env_dims["height"]
    )
    table = bproc.loader.load_blend("./assets/objects/table.blend")[0]

    # Simulation
    floor.enable_rigidbody(active=False, collision_shape="BOX")
    table.enable_rigidbody(active=False, collision_shape="MESH")

    # Materials
    env_mats = create_environment_materials()
    floor_mat = env_mats["floor"]
    wall_mat = env_mats["wall"]
    table_mat = env_mats["table"]

    floor.add_material(material=floor_mat)
    for wall in walls:
        wall.add_material(material=wall_mat)

    table.set_material(index=0, material=table_mat)

    # Create Objects
    objects_on_table = []
    objects_under_table = []

    for j in range(random.randint(1, 2)):
        shape = random.choice(["CUBE", "CYLINDER", "CONE"])
        scale = np.random.uniform(0.14, 0.19)

        obj = create_object(scale=scale, shading_mode="smooth", shape=shape)

        rgba = generate_distinct_rgba()
        material = create_material_for_color(
            obj.get_name(), rgba, np.random.uniform(0.4, 0.6)
        )
        obj.add_material(material)

        on_table = random.random() < 0.5

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
    floor.enable_rigidbody(False)

    bproc.object.simulate_physics_and_fix_final_poses(
        min_simulation_time=2, max_simulation_time=4, check_object_interval=1
    )

    # Camera
    set_intrinsics(512, 512, 40)

    min_cam_location = [-2.5, -2.5, 0.5]
    max_cam_location = [2.5, -1.5, 2.5]
    poi = bproc.object.compute_poi([table] + all_objects)

    for _ in range(5):
        location = sample_camera_location(min_cam_location, max_cam_location)
        cam2world = create_camera_pose(poi, location)
        bproc.camera.add_camera_pose(cam2world)

    # Light
    light = sample_light(poi)

    # Render
    output_path = os.path.join(args.output, next_index_str)
    dirs = prepare_output_dirs(output_path)

    data = render_and_save_hdf5(dirs["hdf5"])

    extract_images_from_hdf5(dirs["hdf5"], dirs)

    # Save Metadata
    metadata = build_metadata(
        floor, walls, table, objects_on_table, objects_under_table, env_dims
    )
    with open(
        os.path.join(output_path, "metadata.json"),
        "w",
    ) as f:
        json.dump(metadata, f, indent=4)

    # Save Prompt
    prompt_data = build_scene_prompt(metadata)
    with open(os.path.join(output_path, "prompt.json"), "w") as f:
        json.dump(prompt_data, f, indent=4)

    bproc.clean_up(clean_up_camera=True)
