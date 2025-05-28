import blenderproc as bproc
import bpy

import argparse
import os
import sys


# Add necessary subdirectories to sys path for Blender
def add_subdirs_to_sys_path(root_dir):
    for dirpath, _, _ in os.walk(root_dir):
        if os.path.basename(dirpath) == "__pycache__":
            continue
        sys.path.append(dirpath)


script_dir = os.path.dirname(os.path.abspath(__file__))
add_subdirs_to_sys_path(script_dir)

from configs.config_loader import load_config
from utils.scene.base_scene import create_scene
from utils.scene.objects import create_objects
from utils.scene.pose_objects import pose_objects
from utils.scene.camera import create_cams
from utils.scene.lighting import create_lighting
from utils.output.render import render
from utils.output.metadata_builder import save_metadata
from utils.output.prompt_builder import save_prompt

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("-i", "--iterations", type=int, default=1)
parser.add_argument("-o", "--output", type=str, help="The output directory")
args = parser.parse_args()
os.makedirs(args.output, exist_ok=True)

# Load config
config = load_config(os.path.abspath("./configs/room.json"))

# BlenderProc
bproc.init()
bproc.renderer.set_max_amount_of_samples(config["render"]["samples"])
bproc.renderer.set_denoiser("OPTIX")
bpy.context.scene.eevee.use_raytracing = True

for i in range(args.iterations):
    # Setup Scene
    env_dims, floor, walls, table = create_scene(config)

    # Create Objects
    objects_on_table, objects_under_table, objects_metadata = create_objects(config)

    # Pose Objects
    objects_on_table, objects_under_table, objects_metadata = pose_objects(
        objects_on_table, objects_under_table, table, floor, objects_metadata
    )

    # Create Camera Poses
    camera_metadata = create_cams(config, table, objects_on_table + objects_under_table)

    # Create Lighting
    light, light_metadata = create_lighting(config, table, env_dims)

    # Render Images
    render(args.output)

    # Save JSON-Outputs
    metadata = save_metadata(
        "room",
        env_dims,
        floor,
        walls,
        table,
        camera_metadata,
        light_metadata,
        objects_metadata,
        args.output,
    )
    prompt = save_prompt("room", objects_metadata, args.output)

    # Clean up
    bproc.clean_up(clean_up_camera=True)
