import blenderproc as bproc
import os
import sys
import argparse
import re
import random
import h5py
import numpy as np
from PIL import Image


# TODO: Surface Pose Sampling/Object Pose Sampling, Camera Sampling/Light Sampling verbessern, Pipeline für Prompts


# Add necessary subdirectories to sys path for Blender
def add_subdirs_to_sys_path(root_dir):
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if os.path.basename(dirpath) == "__pycache__":
            continue
        sys.path.append(dirpath)


script_dir = os.path.dirname(os.path.abspath(__file__))
add_subdirs_to_sys_path(script_dir)

from util.scene.base_scenes.simple_room import generate_simple_room
from util.scene.light import sample_light
from util.scene.camera import create_camera_pose, set_intrinsics, sample_camera_location
from util.obj.mesh import create_object
from util.mat.base import create_object_materials, create_environment_materials
from util.render.lib import normalize_depth, normalize_diffuse, normalize_normals
from util.obj.sample_poses import generate_pose_on_table, generate_pose_under_table

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
    files = [f for f in os.listdir(args.output) if re.match(r"\d{3}", f)]

    if files:
        numbers = [int(re.search(r"\d{3}", f).group()) for f in files]
        next_index = max(numbers) + 1
    else:
        next_index = 0

    next_index_str = f"{next_index:03}"

    scene = generate_simple_room(
        width=random.randint(5, 15), depth=random.randint(5, 15), height=6
    )
    floors = [obj for obj in scene if "Floor" in obj.get_name()]
    walls = [obj for obj in scene if "Wall" in obj.get_name()]

    table = bproc.loader.load_blend("./assets/objects/table.blend")

    floors[0].enable_rigidbody(active=False, collision_shape="BOX")
    table[0].enable_rigidbody(active=False, collision_shape="MESH")

    env_mats = create_environment_materials()
    obj_mats = create_object_materials()

    floor_mat = env_mats["floor"]
    wall_mat = env_mats["wall"]
    floors[0].add_material(material=floor_mat)
    for wall in walls:
        wall.add_material(material=wall_mat)

    table_mat = env_mats["table"]
    table[0].set_material(index=0, material=table_mat)

    objects_on_table = []
    objects_under_table = []

    for j in range(random.randint(1, 5)):
        shape = random.choice(["CUBE", "CYLINDER", "CONE"])

        obj = create_object(
            scale=np.random.uniform(0.1, 0.15), shading_mode="smooth", shape=shape
        )

        obj.add_material(material=random.choice(list(obj_mats.values())))

        if random.random() < 0.5:
            objects_on_table.append(obj)
        else:
            objects_under_table.append(obj)

    if objects_on_table:
        generate_pose_on_table(table[0], objects_on_table)

    if objects_under_table:
        generate_pose_under_table(table[0], floors[0], objects_under_table)

    all_objects = objects_on_table + objects_under_table

    for obj in all_objects:
        obj.enable_rigidbody(True)
    floors[0].enable_rigidbody(False)

    bproc.object.simulate_physics_and_fix_final_poses(
        min_simulation_time=2, max_simulation_time=4, check_object_interval=1
    )

    set_intrinsics(640, 480, 40)

    min_cam_location = [-3, -4, 1]
    max_cam_location = [3, -2, 3]
    poi = bproc.object.compute_poi(table + all_objects)

    for _ in range(5):
        location = sample_camera_location(min_cam_location, max_cam_location)
        cam2world = create_camera_pose(poi, location)
        bproc.camera.add_camera_pose(cam2world)

    light = sample_light(poi)

    data = bproc.renderer.render()

    output_path = os.path.join(args.output, next_index_str)
    hdf5_output_path = os.path.join(output_path, "hdf5")
    colors_output_path = os.path.join(output_path, "colors")
    depth_output_path = os.path.join(output_path, "depth")
    normals_output_path = os.path.join(output_path, "normals")
    diffuse_output_path = os.path.join(output_path, "diffuse")

    bproc.writer.write_hdf5(hdf5_output_path, data)

    for file_name in os.listdir(hdf5_output_path):
        if file_name.endswith(".hdf5"):
            path = os.path.join(hdf5_output_path, file_name)

            with h5py.File(path, "r") as f:
                if "colors" in f:
                    os.makedirs(colors_output_path, exist_ok=True)
                    colors = np.array(f["colors"])
                    if colors.dtype != np.uint8:
                        colors = (colors * 255).clip(0, 255).astype(np.uint8)
                    img = Image.fromarray(colors)
                    img.save(
                        os.path.join(
                            colors_output_path, file_name.replace(".hdf5", ".png")
                        )
                    )

                if "depth" in f:
                    os.makedirs(depth_output_path, exist_ok=True)
                    depth = np.array(f["depth"])
                    depth_img = normalize_depth(depth)
                    img = Image.fromarray(depth_img)
                    img.save(
                        os.path.join(
                            depth_output_path, file_name.replace(".hdf5", ".png")
                        )
                    )

                if "normals" in f:
                    os.makedirs(normals_output_path, exist_ok=True)
                    normals = np.array(f["normals"])
                    normals_img = normalize_normals(normals)
                    img = Image.fromarray(normals_img)
                    img.save(
                        os.path.join(
                            normals_output_path, file_name.replace(".hdf5", ".png")
                        )
                    )

                if "diffuse" in f:
                    os.makedirs(diffuse_output_path, exist_ok=True)
                    diffuse = np.array(f["diffuse"])
                    diffuse_img = normalize_diffuse(diffuse)
                    img = Image.fromarray(diffuse_img)
                    img.save(
                        os.path.join(
                            diffuse_output_path, file_name.replace(".hdf5", ".png")
                        )
                    )

    bproc.clean_up(clean_up_camera=True)
