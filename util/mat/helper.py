import blenderproc as bproc


def import_mats(blend_path):
    existing_material_names = set(
        mat.get_name() for mat in bproc.material.collect_all()
    )

    bproc.loader.load_blend(blend_path, data_blocks=["materials"])

    all_materials = set(bproc.material.collect_all())
    new_materials = [
        mat for mat in all_materials if mat.get_name() not in existing_material_names
    ]

    return list(new_materials)


def adjust_material_mapping_by_scale(obj):
    materials = obj.get_materials()
    original_mat = materials[0]

    mat_copy = original_mat.duplicate()
    obj.set_material(0, mat_copy)

    scale = obj.get_scale()

    for node in mat_copy.nodes:
        if node.type == "MAPPING":
            node.inputs["Scale"].default_value[0] = scale[0]
            node.inputs["Scale"].default_value[1] = scale[1]
