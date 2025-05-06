import numpy as np


def build_metadata(
    floor, walls, table, objects_on_table, objects_under_table, env_dims
):
    def build_object_metadata(obj, position_label):
        return {
            "name": obj.get_name().split(".")[0],
            "position": position_label,
            "location": list(obj.get_location()),
            "rotation": list(obj.get_rotation_euler()),
            "size": get_object_size(obj),
            "material": {
                "base_color": list(
                    obj.get_materials()[0].get_principled_shader_value("Base Color")
                )
            },
        }

    def get_object_size(obj):
        bbox_local = obj.get_bound_box()
        world_matrix = obj.get_local2world_mat()
        bbox_world = [world_matrix @ np.append(corner, 1.0) for corner in bbox_local]
        bbox_world = np.array(bbox_world)[:, :3]
        min_coords = bbox_world.min(axis=0)
        max_coords = bbox_world.max(axis=0)
        size = max_coords - min_coords
        return size.tolist()

    metadata = {
        "environment": "room",
        "env_dimensions": env_dims,
        "floor": {
            "name": floor.get_name(),
            "scale": list(floor.get_scale()),
            "location": list(floor.get_location()),
            "material": list(
                floor.get_materials()[0].get_principled_shader_value("Base Color")
            ),
        },
        "walls": [
            {
                "name": wall.get_name(),
                "scale": list(wall.get_scale()),
                "location": list(wall.get_location()),
                "material": list(
                    wall.get_materials()[0].get_principled_shader_value("Base Color")
                ),
            }
            for wall in walls
        ],
        "table": {
            "name": table.get_name(),
            "scale": list(table.get_scale()),
            "location": list(table.get_location()),
            "material": list(
                table.get_materials()[0].get_principled_shader_value("Base Color")
            ),
        },
        "objects": [
            *[build_object_metadata(obj, "on table") for obj in objects_on_table],
            *[build_object_metadata(obj, "under table") for obj in objects_under_table],
        ],
    }
    return metadata
