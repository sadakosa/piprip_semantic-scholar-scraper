# get the top 50/100 papers for each search term


# SELECT * FROM papers WHERE search_term = 'machine learning' AND num_hops = 0 LIMIT 50 ORDER BY id ASC;

import psycopg2
from db.db_client import DBClient
from db import db_operations
from global_methods import get_search_terms, load_yaml_config
from logger.logger import Logger

# =============================================
# CHECKPOINT FUNCTIONS
# =============================================
import json
import os

def read_checkpoint(checkpoint_file):
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as file:
            return json.load(file).get("last_search_term", 0)
    return 0

def write_checkpoint(checkpoint_file, index):
    with open(checkpoint_file, 'w') as file:
        json.dump({"last_search_term": index}, file)


# =============================================
# SET UP DB, LOGGER AND CHECKPOINT
# =============================================
logger = Logger() # To log last try
logger.log_message("Starting to curate the database")

# ===========psql db connection================
config = load_yaml_config('config/config.yaml')
rds_db = config['RDS_DB']

# PostgreSQL database connection details
psql_user = config['PSQL_USER'] if rds_db else config['LOCAL_PSQL_USER']
psql_password = config['PSQL_PASSWORD'] if rds_db else config['LOCAL_PSQL_PASSWORD']
psql_host = config['PSQL_HOST'] if rds_db else config['LOCAL_PSQL_HOST']
psql_port = config['PSQL_PORT'] if rds_db else config['LOCAL_PSQL_PORT']
psql_read_host = config['PSQL_READ_HOST'] if rds_db else config['LOCAL_PSQL_HOST']

dbclient = DBClient("postgres", psql_user, psql_password, psql_host, psql_port)
# dbclient_read = DBClient("postgres", psql_user, psql_password, psql_read_host, psql_port)

# Set up the database schema
db_operations.create_paper_curated_table(dbclient)
# db_operations.create_references_table(db_client)

# set up checkpoint
checkpoint_file = 'checkpoint.json'
start_term = read_checkpoint(checkpoint_file)

# =============================================
# SEARCH TERMS SETTINGS
# =============================================
csv_file_path = 'search_terms_curated.csv'
search_terms = get_search_terms(csv_file_path) # there are 460 search terms in total
start_term = 0
end_term = 7
num_papers = 50

# for each search term
for idx, search_term in enumerate(search_terms[start_term:end_term]):
    search_term = search_term[0]
    print(f"Processing search term: {search_term}, {idx}")
    logger.log_message(f"Processing search term: {search_term}")
    try:
        # Get the top 50 papers for each search term
        papers = db_operations.get_papers_for_search_term(dbclient, search_term, num_papers)
        
        # Insert the papers into the database
        if papers:
            db_operations.batch_insert_papers(dbclient, papers)

        # Update checkpoint
        write_checkpoint(checkpoint_file, idx + 1)
    
        # Log the search term
        logger.log_message(f"Processed search term: {search_term}, {idx}")

    except Exception as e:
        logger.log_message(f"Error processing search term {search_term}: {e}")
        print(f"Error processing search term {search_term}: {e}")

logger.close_log_file()