import blenderproc as bproc
import numpy as np
import random
import os
import re
import argparse
import json

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

    scene = bproc.loader.load_blend("./resources/scene/scene.blend")
    floor = next(obj for obj in scene if obj.get_name() == "Floor")
    table = bproc.loader.load_blend("./resources/objects/table.blend")[0]
    table.set_location([0, 5, 0])

    floor.enable_rigidbody(active=False, collision_shape="BOX")
    table.enable_rigidbody(active=False, collision_shape="MESH")

    num_objects = random.randint(1, 3)
    objects = []
    for j in range(num_objects):
        pos_type = random.choice(["over", "under"])

        if pos_type == "over":
            obj_pos = np.array(
                [random.uniform(-0.5, 0.5), random.uniform(4.7, 5.3), 1.2]
            )
        elif pos_type == "under":
            obj_pos = np.array(
                [random.uniform(-0.5, 0.5), random.uniform(4.7, 5.3), 0.2]
            )

        object_files = [
            f
            for f in os.listdir("./resources/objects")
            if f.endswith(".blend") and f != "table.blend"
        ]
        blend_path = os.path.join("./resources/objects", random.choice(object_files))

        loaded_objects = bproc.loader.load_blend(blend_path)
        if not loaded_objects:
            continue

        obj = loaded_objects[0]
        obj.set_location(obj_pos)

        rotation_x = np.random.uniform(-90, 90)
        obj.set_rotation_euler([rotation_x, 0, 0])

        # scale = np.random.uniform(0.05, 0.3)
        # obj.set_scale([scale] * 3)

        obj.enable_rigidbody(active=True, collision_shape="BOX")

        objects.append(obj)

    light = bproc.types.Light("POINT")
    light.set_location(
        [random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(1.5, 4)]
    )
    light.set_color(np.random.uniform(0.8, 1.0, 3))
    light.set_energy(random.uniform(100, 2000))

    objects = [table] + objects
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

    bproc.renderer.enable_depth_output(activate_antialiasing=False)
    bproc.renderer.enable_diffuse_color_output()
    bproc.renderer.enable_normals_output()
    data = bproc.renderer.render()
    bproc.writer.write_hdf5(os.path.join("output", next_index_str), data)

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
