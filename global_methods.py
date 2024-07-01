import pyyaml


def load_yaml_config(file_path):
    with open(file_path, 'r') as file:
        config = pyyaml.safe_load(file)
    return config