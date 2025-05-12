import json
from types import SimpleNamespace


def dict_to_namespace(d):
    if isinstance(d, dict):
        ns = SimpleNamespace(
            **{
                k: dict_to_namespace(v) if isinstance(v, dict) else v
                for k, v in d.items()
            }
        )
        return ns
    return d


def load_config(file_path):
    with open(file_path, "r") as f:
        config_dict = json.load(f)
    return dict_to_namespace(config_dict)
