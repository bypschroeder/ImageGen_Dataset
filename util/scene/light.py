import blenderproc as bproc
import numpy as np
import math
import random


def sample_point_light(poi, radius_min=1, radius_max=4, base_energy=1000):

    light = bproc.types.Light(light_type="AREA", name="light")

    light.set_radius(2000000)

    location = bproc.sampler.shell(
        center=[0, 0, 3],
        radius_min=radius_min,
        radius_max=radius_max,
        elevation_min=20,
        elevation_max=80,
    )
    light.set_location(location)

    dist = np.linalg.norm(np.array(location) - np.array(poi))
    light.set_energy(base_energy * 4 / (dist**2))

    return light


def setup_point_lights(env_dims):
    diag = math.sqrt(
        env_dims["width"] ** 2 + env_dims["depth"] ** 2 + env_dims["height"] ** 2
    )

    light_metadata_list = []

    def jitter(val, amount, clamp_min=0.85, clamp_max=1.15):
        return val * min(
            max(1.0 + random.uniform(-amount, amount), clamp_min), clamp_max
        )

    def make_light(
        name,
        base_loc,
        energy_scale,
        radius_scale,
    ):
        light = bproc.types.Light("POINT")
        light.set_location(
            [
                env_dims["width"] * jitter(base_loc[0], 0.2),
                env_dims["depth"] * jitter(base_loc[1], 0.2),
                env_dims["height"] * jitter(base_loc[2], 0.2),
            ]
        )
        light.set_energy(diag * jitter(energy_scale, 0.2))
        light.set_radius(diag * jitter(radius_scale, 0.2))
        light.set_name(name)

        light_metadata_list.append(
            {
                "type": light.get_type(),
                "location": list(light.get_location()),
                "energy": light.get_energy(),
                "radius": light.get_radius(),
            }
        )

        return light

    key_light = make_light(
        "Key_Light", (-0.25, -0.25, 0.9), energy_scale=35, radius_scale=0.1
    )
    fill_light = make_light(
        "Fill_Light", (0.3, -0.25, 0.5), energy_scale=15, radius_scale=0.12
    )
    back_light = make_light(
        "Back_Light", (0.0, 0.5, 0.8), energy_scale=10, radius_scale=0.08
    )
    ambient_light = make_light(
        "Ambient_Light", (0.0, 0.0, 0.2), energy_scale=5, radius_scale=0.8
    )

    return key_light, fill_light, back_light, ambient_light, light_metadata_list


def setup_area_lights(env_dims, poi_obj):
    diag = math.sqrt(
        env_dims["width"] ** 2 + env_dims["depth"] ** 2 + env_dims["height"] ** 2
    )

    light_metadata_list = []

    def jitter_xy(val, amount):
        return val + random.uniform(-amount, amount)

    def make_area_light(name, base_loc, energy_scale, size_scale, jitter_amount=0.15):
        loc = [
            env_dims["width"] * jitter_xy(base_loc[0], jitter_amount),
            env_dims["depth"] * jitter_xy(base_loc[1], jitter_amount),
            env_dims["height"] * base_loc[2],
        ]

        light = bproc.types.Light("AREA")
        light.set_location(loc)
        light.set_energy(
            diag * random.uniform(energy_scale * 0.85, energy_scale * 1.15)
        )

        light_blender_obj = light.blender_obj
        size = diag * random.uniform(size_scale * 0.7, size_scale * 1.3)
        light_blender_obj.data.shape = "RECTANGLE"
        light_blender_obj.data.size = size
        light_blender_obj.data.size_y = size * 0.75

        constraint = light_blender_obj.constraints.new(type="TRACK_TO")
        constraint.target = poi_obj.blender_obj
        constraint.track_axis = "TRACK_NEGATIVE_Z"
        constraint.up_axis = "UP_Y"

        light.set_name(name)

        light_metadata_list.append(
            {
                "type": light.get_type(),
                "location": list(light.get_location()),
                "energy": light.get_energy(),
                "size": [size, size * 0.75],
                "name": name,
            }
        )

        return light

    key_light = make_area_light(
        "Key_Area", (-0.25, -0.25, 0.9), energy_scale=35, size_scale=0.2
    )
    fill_light = make_area_light(
        "Fill_Area", (0.25, -0.25, 0.5), energy_scale=15, size_scale=0.25
    )
    back_light = make_area_light(
        "Back_Area", (0.0, 0.5, 0.8), energy_scale=10, size_scale=0.2
    )
    ambient_light = make_area_light(
        "Ambient_Area",
        (0.0, 0.0, 0.2),
        energy_scale=5,
        size_scale=1.0,
        jitter_amount=0.0,
    )

    return key_light, fill_light, back_light, ambient_light, light_metadata_list


def setup_lights(env_dims, poi_obj, config):
    def jitter(val, amount, clamp_min=0.85, clamp_max=1.15):
        return val * min(
            max(1.0 + random.uniform(-amount, amount), clamp_min), clamp_max
        )

    diag = math.sqrt(
        env_dims["width"] ** 2 + env_dims["depth"] ** 2 + env_dims["height"] ** 2
    )

    jitter_cfg = config["lighting"].get("jitter", {})
    jitter_pos = jitter_cfg.get("position", 0.0)
    jitter_energy = jitter_cfg.get("energy", 0.0)
    jitter_size = jitter_cfg.get("size", 0.0)

    templates = config["lighting"]["templates"]
    template_name = random.choice(list(templates))
    template = templates[template_name]

    created_lights = []
    metadata = {"template": template_name, "lights": []}

    for light_name, light_cfg in template.items():
        base_loc = light_cfg["position"]
        energy_scale = light_cfg["energy_scale"]
        size_scale = light_cfg["size_scale"]

        loc = [
            env_dims["width"] * jitter(base_loc[0], jitter_pos),
            env_dims["depth"] * jitter(base_loc[1], jitter_pos),
            env_dims["height"] * jitter(base_loc[2], jitter_pos),
        ]

        energy = diag * jitter(energy_scale, jitter_energy)
        size = diag * jitter(size_scale, jitter_size)

        light = bproc.types.Light("AREA")
        light.set_location(loc)
        light.set_energy(energy)

        # Set area shape and size
        light.blender_obj.data.shape = "RECTANGLE"
        light.blender_obj.data.size = size
        light.blender_obj.data.size_y = size * 0.75

        # Track to POI
        constraint = light.blender_obj.constraints.new(type="TRACK_TO")
        constraint.target = poi_obj.blender_obj
        constraint.track_axis = "TRACK_NEGATIVE_Z"
        constraint.up_axis = "UP_Y"

        light.set_name(light_name)
        created_lights.append(light)

        metadata["lights"].append(
            {"name": light_name, "location": loc, "energy": energy, "size": size}
        )

    return created_lights, metadata
