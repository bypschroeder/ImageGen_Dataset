import blenderproc as bproc
import numpy as np


def generate_pose_on_table(table, objects):
    def sample_pose_on_table(obj: bproc.types.MeshObject):
        obj.set_location(
            bproc.sampler.upper_region(
                objects_to_sample_on=[table],
                min_height=1,
                max_height=4,
                use_ray_trace_check=False,
            )
        )
        obj.set_rotation_euler([0, 0, np.random.uniform(0, 2 * np.pi)])

    bproc.object.sample_poses_on_surface(
        objects_to_sample=objects,
        surface=table,
        sample_pose_func=sample_pose_on_table,
        min_distance=0.1,
        max_distance=10,
    )


def generate_pose_under_table(table, floor, objects):
    def sample_pose_under_table(obj: bproc.types.MeshObject):
        table_bbox = table.get_bound_box()
        x_min, y_min = np.min(table_bbox[:, :2], axis=0)
        x_max, y_max = np.max(table_bbox[:, :2], axis=0)

        x = np.random.uniform(x_min, x_max)
        y = np.random.uniform(y_min, y_max)

        z = floor.get_location()[2] + 0.02

        obj.set_location([x, y, z])
        obj.set_rotation_euler([0, 0, np.random.uniform(0, 2 * np.pi)])

    bproc.object.sample_poses_on_surface(
        objects_to_sample=objects,
        surface=floor,
        sample_pose_func=sample_pose_under_table,
        min_distance=0.1,
        max_distance=10,
    )
