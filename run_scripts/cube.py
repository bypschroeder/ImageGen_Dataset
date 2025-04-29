import blenderproc as bproc
import numpy as np
import random
import os
import re
import argparse
import json
import h5py
from PIL import Image

# from util.scene.generate_simple_room import generate_simple_room


def generate_simple_room(width=10.0, depth=8.0, height=3.0):
    room_objects = []

    floor = bproc.object.create_primitive(
        "PLANE",
        scale=[width / 2.0, depth / 2.0, 1],
        location=[0, 0, 0],
        rotation=[0, 0, 0],
    )
    floor.set_name("Floor")
    room_objects.append(floor)

    wall_back = bproc.object.create_primitive(
        "PLANE",
        scale=[width / 2.0, height / 2.0, 1],
        location=[0, -depth / 2.0, height / 2.0],
        rotation=[np.pi / 2, 0, 0],
    )
    wall_back.set_name("Wall_Back")
    room_objects.append(wall_back)

    wall_front = bproc.object.create_primitive(
        "PLANE",
        scale=[width / 2.0, height / 2.0, 1],
        location=[0, depth / 2.0, height / 2.0],
        rotation=[np.pi / 2, 0, 0],
    )
    wall_front.set_name("Wall_Front")
    room_objects.append(wall_front)

    wall_left = bproc.object.create_primitive(
        "PLANE",
        scale=[depth / 2.0, height / 2.0, 1],
        location=[-width / 2.0, 0, height / 2.0],
        rotation=[np.pi / 2, 0, np.pi / 2],
    )
    wall_left.set_name("Wall_Left")
    room_objects.append(wall_left)

    wall_right = bproc.object.create_primitive(
        "PLANE",
        scale=[depth / 2.0, height / 2.0, 1],
        location=[width / 2.0, 0, height / 2.0],
        rotation=[np.pi / 2, 0, np.pi / 2],
    )
    wall_right.set_name("Wall_Right")
    room_objects.append(wall_right)

    return room_objects


def normalize_depth(depth):
    depth_min = np.min(depth)
    depth_max = np.max(depth)
    if depth_max - depth_min == 0:
        return np.zeros_like(depth, dtype=np.uint8)
    depth_norm = (depth - depth_min) / (depth_max - depth_min)
    return (depth_norm * 255).astype(np.uint8)


def normalize_normals(normals):
    normals = ((normals + 1.0) / 2.0 * 255.0).clip(0, 255).astype(np.uint8)
    return normals


bproc.renderer.enable_depth_output(activate_antialiasing=False)
bproc.renderer.enable_normals_output()
bproc.renderer.set_noise_threshold(0.01)


output_dir = "./output"
os.makedirs(output_dir, exist_ok=True)

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--iterations", type=int)
args = parser.parse_args()

bproc.init()

for i in range(args.iterations):
    files = [f for f in os.listdir(output_dir) if re.match(r"\d{3}", f)]

    if files:
        numbers = [int(re.search(r"\d{3}", f).group()) for f in files]
        next_index = max(numbers) + 1
    else:
        next_index = 0

    next_index_str = f"{next_index:03}"

    scene = generate_simple_room(width=20, depth=20, height=3)

    # scene = bproc.loader.load_blend("./resources/scene/scene.blend")
    floor = next(obj for obj in scene if obj.get_name() == "Floor")
    table = bproc.loader.load_blend("./assets/objects/table.blend")[0]
    table.set_location([0, 5, 0])

    floor.enable_rigidbody(active=False, collision_shape="BOX")
    table.enable_rigidbody(active=False, collision_shape="MESH")

    num_cubes = random.randint(1, 5)
    cubes = []
    for j in range(num_cubes):
        pos_type = random.choice(["over", "under"])

        if pos_type == "over":
            cube_pos = np.array(
                [random.uniform(-0.5, 0.5), random.uniform(4.7, 5.3), 1.2]
            )
        elif pos_type == "under":
            cube_pos = np.array(
                [random.uniform(-0.5, 0.5), random.uniform(4.7, 5.3), 0.2]
            )

        cube = bproc.object.create_primitive("CUBE")
        cube.set_location(cube_pos)

        rotation_x = np.random.uniform(-90, 90)
        cube.set_rotation_euler([rotation_x, 0, 0])

        scale = np.random.uniform(0.1, 0.2)
        cube.set_scale([scale] * 3)
        cube.enable_rigidbody(active=True, collision_shape="BOX")

        mat = bproc.material.create("cube_material_" + str(j))

        colors = {
            "black": [0.0, 0.0, 0.0, 1.0],
            "white": [1.0, 1.0, 1.0, 1.0],
            "red": [1.0, 0.0, 0.0, 1.0],
            "green": [0.0, 1.0, 0.0, 1.0],
            "blue": [0.0, 0.0, 1.0, 1.0],
            "yellow": [1.0, 1.0, 0.0, 1.0],
            "cyan": [0.0, 1.0, 1.0, 1.0],
            "magenta": [1.0, 0.0, 1.0, 1.0],
            "gray": [0.5, 0.5, 0.5, 1.0],
            "orange": [1.0, 0.65, 0.0, 1.0],
            "pink": [1.0, 0.75, 0.8, 1.0],
            "purple": [0.5, 0.0, 0.5, 1.0],
            "violet": [0.93, 0.51, 0.93, 1.0],
            "brown": [0.65, 0.16, 0.16, 1.0],
        }

        random_color_name = random.choice(list(colors.keys()))
        mat.set_principled_shader_value("Base Color", colors[random_color_name])
        mat.set_principled_shader_value("Roughness", np.random.uniform(0.1, 1.0))
        mat.set_principled_shader_value("Metallic", np.random.uniform(0.0, 1.0))
        cube.replace_materials(mat)

        cubes.append(cube)

    light = bproc.types.Light("POINT")
    light.set_location(
        [random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(1.5, 4)]
    )
    light.set_color(np.random.uniform(0.8, 1.0, 3))
    light.set_energy(random.uniform(100, 2000))

    objects = [table] + cubes
    poi = bproc.object.compute_poi(objects)
    for _ in range(5):
        cam_pos_type = random.choice(
            ["left", "right", "top", "bottom", "front", "back"]
        )

        if cam_pos_type == "left":
            location = np.array(
                [
                    random.uniform(-3, -1),
                    random.uniform(-1.5, 1.5),
                    random.uniform(1.5, 3.0),
                ]
            )
        elif cam_pos_type == "right":
            location = np.array(
                [
                    random.uniform(1, 3),
                    random.uniform(-1.5, 1.5),
                    random.uniform(1.5, 3.0),
                ]
            )
        elif cam_pos_type == "top":
            location = np.array(
                [
                    random.uniform(-1.5, 1.5),
                    random.uniform(-1.5, 1.5),
                    random.uniform(3.0, 4.0),
                ]
            )
        elif cam_pos_type == "bottom":
            location = np.array(
                [
                    random.uniform(-1.5, 1.5),
                    random.uniform(-1.5, 1.5),
                    random.uniform(0.1, 1.5),
                ]
            )
        elif cam_pos_type == "front":
            location = np.array(
                [
                    random.uniform(-1.5, 1.5),
                    random.uniform(-3, -1),
                    random.uniform(1.5, 3.0),
                ]
            )
        elif cam_pos_type == "back":
            location = np.array(
                [
                    random.uniform(-1.5, 1.5),
                    random.uniform(1, 3),
                    random.uniform(1.5, 3.0),
                ]
            )

        rotation_matrix = bproc.camera.rotation_from_forward_vec(poi - location)
        cam2world = bproc.math.build_transformation_mat(location, rotation_matrix)
        bproc.camera.add_camera_pose(cam2world)

    bproc.object.simulate_physics_and_fix_final_poses(
        min_simulation_time=4, max_simulation_time=20, check_object_interval=1
    )

    data = bproc.renderer.render()

    output_path = os.path.join(output_dir, next_index_str)
    hdf5_output_path = os.path.join(output_path, "hdf5")
    colors_output_path = os.path.join(output_path, "colors")
    depth_output_path = os.path.join(output_path, "depth")
    normals_output_path = os.path.join(output_path, "normals")
    os.makedirs(hdf5_output_path, exist_ok=True)

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

    # if scale >= 0.05 and scale < 0.1:
    #     size = "small"
    # elif scale > 0.1 and scale <= 0.2:
    #     size = "medium"
    # elif scale > 0.2:
    #     size = "large"

    # if pos_type == "over":
    #     pos = "on"
    # elif pos_type == "under":
    #     pos = "under"

    # prompt_variants = [
    #     f"A {size} {random_color_name} cube placed {pos} a table",
    #     f"A {random_color_name} cube of {size} size is placed {pos} a table",
    #     f"Placed on the table is a {size} {random_color_name} cube",
    #     f"A {size} cube with {random_color_name} color is placed {pos} a table",
    # ]

    # json_data = {"prompts": prompt_variants}

    # with open(os.path.join("output", next_index_str, "prompts.json"), "w") as f:
    #     json.dump(json_data, f)

    bproc.clean_up(clean_up_camera=True)
