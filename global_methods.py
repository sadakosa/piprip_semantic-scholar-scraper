import yaml
from urllib.parse import quote
import json
import os



def load_yaml_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def make_url_friendly(term):
    return quote(term)


# ====================================================================================================
# Checkpoint Functions
# ====================================================================================================

CHECKPOINT_FILE = 'checkpoint.json'

def save_checkpoint_scrape(search_term, current_page, last_processed_item):
    checkpoint = {
        'search_term': search_term,
        'current_page': current_page,
        'last_processed_item': last_processed_item
    }
    with open(CHECKPOINT_FILE, 'w') as file:
        json.dump(checkpoint, file)

def load_checkpoint_scrape():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r') as file:
            return json.load(file)
    return None




def load_checkpoint_references():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r') as file:
            return json.load(file)
    return None

def save_checkpoint_references(checkpoint):
    with open(CHECKPOINT_FILE, 'w') as file:
        json.dump(checkpoint, file)




