import blenderproc as bproc
import numpy as np


def generate_simple_room(env_dims):
    floor = bproc.object.create_primitive(
        "PLANE",
        scale=[env_dims["width"] / 2.0, env_dims["depth"] / 2.0, 1],
        location=[0, 0, 0],
        rotation=[0, 0, 0],
    )
    floor.set_name("Floor")

    ceiling = bproc.object.create_primitive(
        "PLANE",
        scale=[env_dims["width"] / 2.0, env_dims["depth"] / 2.0, 1],
        location=[0, 0, env_dims["height"]],
        rotation=[0, 0, 0],
    )
    ceiling.set_name("Ceiling")

    wall_front = bproc.object.create_primitive(
        "PLANE",
        scale=[env_dims["width"] / 2.0, env_dims["height"] / 2.0, 1],
        location=[0, env_dims["depth"] / 2.0, env_dims["height"] / 2.0],
        rotation=[np.pi / 2, 0, 0],
    )
    wall_front.set_name("Wall_Front")

    wall_left = bproc.object.create_primitive(
        "PLANE",
        scale=[env_dims["depth"] / 2.0, env_dims["height"] / 2.0, 1],
        location=[-env_dims["width"] / 2.0, 0, env_dims["height"] / 2.0],
        rotation=[np.pi / 2, 0, np.pi / 2],
    )
    wall_left.set_name("Wall_Left")

    wall_right = bproc.object.create_primitive(
        "PLANE",
        scale=[env_dims["depth"] / 2.0, env_dims["height"] / 2.0, 1],
        location=[env_dims["width"] / 2.0, 0, env_dims["height"] / 2.0],
        rotation=[np.pi / 2, 0, np.pi / 2],
    )
    wall_right.set_name("Wall_Right")

    walls = [wall_front, wall_left, wall_right]

    return floor, ceiling, walls
