import blenderproc as bproc
import numpy as np


def set_intrinsics(image_width, image_height, focal_length):
    fx = focal_length * image_width / 50
    fy = fx
    cx = image_width / 2
    cy = image_height / 2

    K = np.array([[fx, 0, cx], [0, fy, cy], [0, 0, 1]])

    bproc.camera.set_intrinsics_from_K_matrix(K, image_width, image_height)


def create_camera_pose(poi, location):
    rotation_matrix = bproc.camera.rotation_from_forward_vec(
        poi - location, inplane_rot=np.random.uniform(-np.pi / 32, np.pi / 32)
    )
    cam2world = bproc.math.build_transformation_mat(location, rotation_matrix)

    return cam2world


def sample_camera_location(min_location, max_location):
    min_location = np.array(min_location)
    max_location = np.array(max_location)

    location = np.random.uniform(min_location, max_location)

    return location
