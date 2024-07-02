import yaml
from urllib.parse import quote


def load_yaml_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def make_url_friendly(term):
    return quote(term)
