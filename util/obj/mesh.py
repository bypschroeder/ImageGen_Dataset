import blenderproc as bproc
import numpy as np
import random


def create_object(
    scale=0.1,
    shading_mode="smooth",
    shape="CUBE",
):
    obj = bproc.object.create_primitive(shape, scale=[scale] * 3)

    obj.set_shading_mode(shading_mode)

    return obj


# def sample_pose(
#     obj: bproc.types.MeshObject,
# ):
#     obj.set_location(np.random.uniform([-0.5, -0.5, 0.1], [0.5, 0.5, 2]))
#     obj.set_rotation_euler(bproc.sampler.uniformSO3())
