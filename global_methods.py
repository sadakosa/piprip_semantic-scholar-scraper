import yaml
from urllib.parse import quote, unquote
import json
import os
import csv



def load_yaml_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
    return config

def make_url_friendly(term):
    return quote(term)

def undo_url_friendly(url_friendly_term):
    return unquote(url_friendly_term)

def get_search_terms():
    csv_file_path = 'search_terms.csv'
    search_terms = []

    with open(csv_file_path, mode='r') as file: # open the csv file, read
        # Create a CSV reader object
        csv_reader = csv.reader(file)
        
        # Iterate over each row in the CSV file
        for row in csv_reader:
            # Append each row to the data array
            search_terms.append(row)
    return search_terms





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

def remove_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        os.remove(CHECKPOINT_FILE)




# def load_checkpoint_references():
#     if os.path.exists(CHECKPOINT_FILE):
#         with open(CHECKPOINT_FILE, 'r') as file:
#             return json.load(file)
#     return None

def load_checkpoint_references():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError as e:
                print(f"Error loading JSON from checkpoint file: {e}")
                return None
    return None

def save_checkpoint_references(checkpoint):
    with open(CHECKPOINT_FILE, 'w') as file:
        json.dump(checkpoint, file)




