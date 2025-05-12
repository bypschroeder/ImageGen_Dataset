import blenderproc as bproc
import numpy as np


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
