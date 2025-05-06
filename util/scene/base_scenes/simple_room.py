import blenderproc as bproc
import numpy as np


def generate_simple_room(width=10.0, depth=8.0, height=3.0):
    floor = bproc.object.create_primitive(
        "PLANE",
        scale=[width / 2.0, depth / 2.0, 1],
        location=[0, 0, 0],
        rotation=[0, 0, 0],
    )
    floor.set_name("Floor")

    # # wall_back = bproc.object.create_primitive(
    # #     "PLANE",
    # #     scale=[width / 2.0, height / 2.0, 1],
    # #     location=[0, -depth / 2.0, height / 2.0],
    # #     rotation=[np.pi / 2, 0, 0],
    # # )
    # # wall_back.set_name("Wall_Back")

    wall_front = bproc.object.create_primitive(
        "PLANE",
        scale=[width / 2.0, height / 2.0, 1],
        location=[0, depth / 2.0, height / 2.0],
        rotation=[np.pi / 2, 0, 0],
    )
    wall_front.set_name("Wall_Front")

    wall_left = bproc.object.create_primitive(
        "PLANE",
        scale=[depth / 2.0, height / 2.0, 1],
        location=[-width / 2.0, 0, height / 2.0],
        rotation=[np.pi / 2, 0, np.pi / 2],
    )
    wall_left.set_name("Wall_Left")

    wall_right = bproc.object.create_primitive(
        "PLANE",
        scale=[depth / 2.0, height / 2.0, 1],
        location=[width / 2.0, 0, height / 2.0],
        rotation=[np.pi / 2, 0, np.pi / 2],
    )
    wall_right.set_name("Wall_Right")

    walls = [wall_front, wall_left, wall_right]

    return floor, walls
