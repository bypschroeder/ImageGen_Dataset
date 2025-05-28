import blenderproc as bproc
import random
import os

from utils.scene.materials import import_mats


def create_object(
    scale=0.1,
    shading_mode="smooth",
    shape="CUBE",
):
    obj = bproc.object.create_primitive(shape, scale=[scale] * 3)

    obj.set_shading_mode(shading_mode)

    return obj


def create_objects(config):
    obj_mats = import_mats(os.path.abspath(config["materials"]["objects"]))

    objects_on_table = []
    objects_under_table = []
    objects_metadata = []

    for i in range(
        random.randint(
            config["objects"]["min_objects"], config["objects"]["max_objects"]
        )
    ):
        shape = random.choice(["CUBE", "CYLINDER", "CONE", "SPHERE"])
        size_name, size_value = random.choice(
            list(config["objects"]["size_options"].items())
        )
        obj = create_object(scale=size_value, shading_mode="smooth", shape=shape)

        on_table = random.random() < config["objects"]["location_rate"]

        if on_table:
            objects_on_table.append(obj)
        else:
            objects_under_table.append(obj)

        mat = random.choice(obj_mats)
        obj.add_material(mat)

        objects_metadata.append(
            {
                "shape": shape,
                "size": {
                    "name": size_name,
                    "value": size_value,
                },
                "material": mat.get_name().split(".")[0] if mat else "no material",
                "position": {
                    "name": "on table" if on_table else "under table",
                    "coordinates": None,
                },
            }
        )

    return objects_on_table, objects_under_table, objects_metadata
