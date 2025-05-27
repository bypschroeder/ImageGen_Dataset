import json
from types import SimpleNamespace


def load_config(file_path):
    with open(file_path, "r") as f:
        config_dict = json.load(f)
    return config_dict
