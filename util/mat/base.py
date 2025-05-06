import blenderproc as bproc
import random
import webcolors


def create_environment_materials():
    colors = {
        "floor": [0.15, 0.15, 0.15, 1.0],
        "wall": [0.9, 0.9, 0.9, 1.0],
        "table": [0.45, 0.30, 0.20, 1.0],
    }

    materials = {}

    for color_name, color_value in colors.items():
        material = bproc.material.create(name=f"{color_name}_matte")
        material.set_principled_shader_value("Base Color", color_value)
        material.set_principled_shader_value("Roughness", 1.0)
        materials[f"{color_name}"] = material

    return materials


def create_object_materials():
    colors = {
        "brown": [0.35, 0.25, 0.20, 1.0],
        "gray": [0.5, 0.5, 0.5, 1.0],
        "red": [1.0, 0.0, 0.0, 1.0],
        "green": [0.0, 1.0, 0.0, 1.0],
        "blue": [0.0, 0.0, 1.0, 1.0],
        "yellow": [1.0, 1.0, 0.0, 1.0],
        "cyan": [0.0, 1.0, 1.0, 1.0],
        "orange": [1.0, 0.65, 0.0, 1.0],
        "pink": [1.0, 0.75, 0.8, 1.0],
        "purple": [0.5, 0.0, 0.5, 1.0],
    }

    materials = {}

    for color_name, color_value in colors.items():
        matte_material = bproc.material.create(name=f"{color_name}_matte")
        matte_material.set_principled_shader_value("Base Color", color_value)
        matte_material.set_principled_shader_value("Roughness", 1.0)

        shiny_material = bproc.material.create(name=f"{color_name}_shiny")
        shiny_material.set_principled_shader_value("Base Color", color_value)
        shiny_material.set_principled_shader_value("Roughness", 0.0)

        materials[f"{color_name}_matte"] = matte_material
        materials[f"{color_name}_shiny"] = shiny_material

    return materials


def create_material_for_color(name, rgba, roughness):
    mat = bproc.material.create(name)
    mat.set_principled_shader_value("Base Color", rgba)
    mat.set_principled_shader_value("Roughness", roughness)

    return mat


def generate_distinct_rgba():
    css21_colors = webcolors.names("css21")
    random_color_name = random.choice(css21_colors)
    rgb = webcolors.name_to_rgb(random_color_name)
    rgba = [rgb.red / 255, rgb.green / 255, rgb.blue / 255, 1.0]

    return rgba
