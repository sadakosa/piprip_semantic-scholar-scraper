import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


from logger.logger import Logger
from db.db_client import DBClient
from global_methods import load_yaml_config, make_url_friendly
from db import db_operations

# from random_1 import extract_abstract_test
from crawler import Crawler



# ====================================================================================================
# Checkpoint Functions
# ====================================================================================================

import json
import os

CHECKPOINT_FILE = 'checkpoint.json'

def save_checkpoint(search_term, current_page, last_processed_item):
    checkpoint = {
        'search_term': search_term,
        'current_page': current_page,
        'last_processed_item': last_processed_item
    }
    with open(CHECKPOINT_FILE, 'w') as file:
        json.dump(checkpoint, file)

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE, 'r') as file:
            return json.load(file)
    return None







# ====================================================================================================
# First Scrapping Method - Search and Scrape
# ====================================================================================================

def search_and_scrape(term, start_page, end_page, logger, db_client):

    # Load the checkpoint if it exists
    checkpoint = load_checkpoint()
    if checkpoint:
        start_page = checkpoint['current_page']
        term = checkpoint['search_term']
        

    checkpoint = load_checkpoint()
    if checkpoint and checkpoint['search_term'] == term:
        start_page = checkpoint['current_page']
        last_processed_item = checkpoint['last_processed_item']
        logger.log_message(f"Resuming search from page {start_page} for search term {term}")
    else:
        last_processed_item = -1


    # Setup WebDriver (e.g., ChromeDriver)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode for faster execution
    driver = webdriver.Chrome(options=options)
    driver.delete_cookie('IS_SELENIUM')
    time.sleep(1)

    crawler = Crawler(logger, db_client, driver)

    base_url = "https://www.semanticscholar.org"
    search_url = f"{base_url}/search?fos%5B0%5D=computer-science&q={term}&sort=total-citations&page="
    
    for current_page in range(start_page, end_page + 1):
        try:
            driver.get(search_url + str(current_page))

            # Wait for the search results to load (adjust the timeout as needed)
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "cl-paper-row"))
            )
            
            crawler.close_cookie_banner()
            time.sleep(5)

            
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            results = soup.find_all('div', class_='cl-paper-row') # rows of search results (1 row = 1 result)

            if not results:
                # print(f"No results found on page {current_page}. Ending search.")
                logger.log_message(f"No results found on page {current_page} for search term {term}. Ending search.")
                break  # Exit the loop if no results are found (end of pages)
            
            # Extract and print the information from each result
            for i, result in enumerate(results):

                if current_page == start_page and i <= last_processed_item:
                    continue  # Skip already processed items

                # logger.log_message("result: " + str(result))

                try:
                    title, ss_id = crawler.extract_title_and_ss_id(result)
                    abstract = crawler.extract_abstract(result, i, ss_id)
                    paper_url = "https://www.semanticscholar.org/paper/" + ss_id

                    # Insert the paper into the database
                    db_operations.insert_paper(db_client, ss_id, title, abstract, paper_url)
                    # print(f"Title: {title}\nPaper ID: {ss_id}\nAbstract: {abstract}")
                except AttributeError as e:
                    # print(f"Error parsing result: {e}")
                    logger.log_message(f"Error parsing result for result {i} on page {current_page}, search term {term}. Error: {e}")
                
                # Save the checkpoint after processing each item
                save_checkpoint(term, current_page, i)

            # Record the last successful trial
            logger.log_message(f"Last successful trial: Current Page [{current_page}], Search Term [{term}], Date-Time [{time.ctime()}]")
            # Be polite and wait a bit before the next request to avoid being blocked
            time.sleep(1)        

        except Exception as e:
            # print(f"An error occurred on page {current_page}: {e}")
            logger.log_message(f"An error occurred on page {current_page} for search term {term}. Error: {e}")
            logger.log_message(f"Last successful trial: Current Page [{current_page}], Search Term [{term}]")
            break  # Optionally, you can choose to retry or skip this page
    
    driver.quit()

    # Remove the checkpoint file after successful completion
    if current_page == end_page:
        os.remove(CHECKPOINT_FILE)









# ====================================================================================================
# Second Scrapping Method - Scrape References & Citations
# ====================================================================================================



def scrape_references(logger, db_client):
    crawler = Crawler(logger, db_client)

    paper_id = "56cd42350c3542c22ecc69f50ccc7bab241e6687"
    crawler.extract_references(paper_id)

    # paper_ids = db_operations.get_all_paper_ids(db_client)

    # for paper_id in paper_ids:
    #     try:
    #         crawler.extract_references(paper_id)
    #     except Exception as e:
    #         logger.log_message(f"An error occurred while extracting references for paper {paper_id}. Error: {e}")





def main():
    logger = Logger() # To log last try

    # =============================================
    # POSTGRESQL DATABASE CONNECTION
    # =============================================

    config = load_yaml_config('config/config.yaml')
    # AWS RDS PostgreSQL database connection details
    # psql_user = config['PSQL_USER']
    # psql_password = config['PSQL_PASSWORD']
    # psql_host = config['PSQL_HOST']
    # psql_port = config['PSQL_PORT']

    # Local PostgreSQL database connection details
    psql_user = config['LOCAL_PSQL_USER']
    psql_password = config['LOCAL_PSQL_PASSWORD']
    psql_host = config['LOCAL_PSQL_HOST']
    psql_port = config['LOCAL_PSQL_PORT']
    db_client = DBClient("postgres", psql_user, psql_password, psql_host, psql_port)

    # Set up the database schema
    db_operations.create_paper_table(db_client)
    db_operations.create_references_table(db_client)

    # =============================================
    # SEARCH AND SCRAPE
    # =============================================

    # Example usage
    start_page = 2
    end_page = 4
    search_term = "information retrieval"
    parsed_search_term = make_url_friendly(search_term)
    search_and_scrape(parsed_search_term, start_page, end_page, logger, db_client)

    # =============================================
    # SCRAPE REFERENCES
    # =============================================

    # scrape_references(logger, db_client)
    
    logger.close_log_file()

if __name__ == "__main__":
    main()
