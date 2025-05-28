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


def create_cams(config, table, objects):
    set_intrinsics(
        config["render"]["resolution_x"],
        config["render"]["resolution_y"],
        config["camera"]["focal_length"],
    )

    poi = bproc.object.compute_poi([table] + objects)

    for i in range(config["camera"]["num_poses"]):
        location = sample_camera_location(
            config["camera"]["location"]["min"], config["camera"]["location"]["max"]
        )
        cam2world = create_camera_pose(poi, location)
        bproc.camera.add_camera_pose(cam2world)

    camera_metadata = {
        "resolution": {
            "x": config["render"]["resolution_x"],
            "y": config["render"]["resolution_y"],
        },
        "focal_length": config["camera"]["focal_length"],
        "point_of_interest": poi.tolist(),
        "camera_locations": [
            bproc.camera.get_camera_pose(i)[:3, 3].tolist()
            for i in range(config["camera"]["num_poses"])
        ],
    }

    return camera_metadata
