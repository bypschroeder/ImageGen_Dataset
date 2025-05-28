import blenderproc as bproc
import random
import os
import numpy as np

from utils.scene.materials import import_mats, adjust_material_mapping_by_scale


def generate_simple_room(env_dims, room_offset_y=-1.0):
    floor = bproc.object.create_primitive(
        "PLANE",
        scale=[env_dims["width"] / 2.0, env_dims["depth"] / 2.0, 1],
        location=[0, room_offset_y, 0],
        rotation=[0, 0, 0],
    )
    floor.set_name("Floor")

    # ceiling = bproc.object.create_primitive(
    #     "PLANE",
    #     scale=[env_dims["width"] / 2.0, env_dims["depth"] / 2.0, 1],
    #     location=[0, room_offset_y, env_dims["height"]],
    #     rotation=[0, 0, 0],
    # )
    # ceiling.set_name("Ceiling")

    wall_front = bproc.object.create_primitive(
        "PLANE",
        scale=[env_dims["width"] / 2.0, env_dims["height"] / 2.0, 1],
        location=[0, env_dims["depth"] / 2.0 + room_offset_y, env_dims["height"] / 2.0],
        rotation=[np.pi / 2, 0, 0],
    )
    wall_front.set_name("Wall_Front")

    wall_left = bproc.object.create_primitive(
        "PLANE",
        scale=[env_dims["depth"] / 2.0, env_dims["height"] / 2.0, 1],
        location=[-env_dims["width"] / 2.0, room_offset_y, env_dims["height"] / 2.0],
        rotation=[np.pi / 2, 0, np.pi / 2],
    )
    wall_left.set_name("Wall_Left")

    wall_right = bproc.object.create_primitive(
        "PLANE",
        scale=[env_dims["depth"] / 2.0, env_dims["height"] / 2.0, 1],
        location=[env_dims["width"] / 2.0, room_offset_y, env_dims["height"] / 2.0],
        rotation=[np.pi / 2, 0, np.pi / 2],
    )
    wall_right.set_name("Wall_Right")

    walls = [wall_front, wall_left, wall_right]

    return floor, walls


def create_scene(config):
    env_dims = {
        "width": random.randint(
            config["room"]["width"]["min"], config["room"]["width"]["max"]
        ),
        "depth": random.randint(
            config["room"]["depth"]["min"], config["room"]["depth"]["max"]
        ),
        "height": config["room"]["height"],
    }

    floor, walls = generate_simple_room(env_dims, room_offset_y=-1)
    floor.enable_rigidbody(active=False, collision_shape="BOX")

    table = bproc.loader.load_blend("./assets/objects/table.blend")[0]

    floor_mats = import_mats(os.path.abspath(config["materials"]["env"]["floor"]))
    wall_mats = import_mats(os.path.abspath(config["materials"]["env"]["wall"]))
    table_mats = import_mats(os.path.abspath(config["materials"]["env"]["table"]))

    floor_mat = random.choice(floor_mats)
    floor.add_material(floor_mat)
    adjust_material_mapping_by_scale(floor)

    wall_mat = random.choice(wall_mats)
    for wall in walls:
        wall.add_material(wall_mat)
        adjust_material_mapping_by_scale(wall)

    tabletop_mat = random.choice(table_mats)
    tableleg_mat = random.choice([mat for mat in table_mats if mat != tabletop_mat])
    table.set_material(index=0, material=tableleg_mat)
    table.set_material(index=1, material=tabletop_mat)

    return env_dims, floor, walls, table
