import blenderproc as bproc
import numpy as np


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

    # # wall_back = bproc.object.create_primitive(
    # #     "PLANE",
    # #     scale=[width / 2.0, height / 2.0, 1],
    # #     location=[0, -depth / 2.0, height / 2.0],
    # #     rotation=[np.pi / 2, 0, 0],
    # # )
    # # wall_back.set_name("Wall_Back")
    # room_objects.append(wall_back)

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
