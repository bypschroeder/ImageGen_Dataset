import blenderproc as bproc
import numpy as np


def generate_pose_on_table(table, objects, margin=0.1, min_height=1, max_height=2):
    def sample_pose_on_table(obj: bproc.types.MeshObject):
        table_bbox = table.get_bound_box()
        x_min, y_min = np.min(table_bbox[:, :2], axis=0)
        x_max, y_max = np.max(table_bbox[:, :2], axis=0)

        x = np.random.uniform(x_min + margin, x_max - margin)
        y = np.random.uniform(y_min + margin, y_max - margin)
        z = np.random.uniform(min_height, max_height)

        obj.set_location([x, y, z])
        obj.set_rotation_euler([0, 0, np.random.uniform(0, 2 * np.pi)])

    bproc.object.sample_poses_on_surface(
        objects_to_sample=objects,
        surface=table,
        sample_pose_func=sample_pose_on_table,
        min_distance=0.1,
        max_distance=1,
    )


def generate_pose_under_table(table, floor, objects, margin=0.1):
    def sample_pose_under_table(obj: bproc.types.MeshObject):
        table_bbox = table.get_bound_box()
        x_min, y_min = np.min(table_bbox[:, :2], axis=0)
        x_max, y_max = np.max(table_bbox[:, :2], axis=0)

        x = np.random.uniform(x_min + margin, x_max - margin)
        y = np.random.uniform(y_min + margin, y_max - margin)

        z = floor.get_location()[2] + 0.02

        obj.set_location([x, y, z])
        obj.set_rotation_euler([0, 0, np.random.uniform(0, 2 * np.pi)])

    bproc.object.sample_poses_on_surface(
        objects_to_sample=objects,
        surface=floor,
        sample_pose_func=sample_pose_under_table,
        min_distance=0.1,
        max_distance=1,
    )


def pose_objects(objects_on_table, objects_under_table, table, floor, objects_metadata):
    if objects_on_table:
        generate_pose_on_table(table, objects_on_table, margin=0.2)

    if objects_under_table:
        generate_pose_under_table(table, floor, objects_under_table, margin=0.2)

    all_objects = objects_on_table + objects_under_table

    for obj in all_objects:
        obj.enable_rigidbody(True)

    bproc.object.simulate_physics_and_fix_final_poses(
        min_simulation_time=2, max_simulation_time=4, check_object_interval=1
    )

    for obj_metadata, obj in zip(objects_metadata, all_objects):
        coordinates = obj.get_location()
        obj_metadata["position"]["coordinates"] = coordinates.tolist()

    return objects_on_table, objects_under_table, objects_metadata
