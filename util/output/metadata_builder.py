def build_metadata(environment, env_dims, floor, walls, table, camera, light, objects):
    metadata = {
        "environment": environment,
        "env_dimensions": env_dims,
        "env_materials": {
            "floor_material": floor.get_materials()[0].get_name().split(".")[0],
            "wall_material": walls[0].get_materials()[0].get_name().split(".")[0],
            "table_material": table.get_materials()[1].get_name().split(".")[0],
        },
        "camera": camera,
        "light": light,
        "objects": objects,
    }
    return metadata
