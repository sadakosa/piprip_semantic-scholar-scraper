import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options


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

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-extensions")
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



def scrape_references_and_citations(logger, db_client, start_paper, end_paper):
    crawler = Crawler(logger, db_client)

    references_and_citations = crawler.extract_references_and_citations(start_paper, end_paper)
    references_and_citations_string = json.dumps(references_and_citations)
    logger.log_message(f"References and Citations: {references_and_citations_string}")

    # get an array of the keys in the references_and_citations dictionary
    paper_ids = references_and_citations.keys()

    # # iterate through the paper_ids and extract the paperId, title, and abstract
    # for paper_id in paper_ids:
    #     title, abstract = references_and_citations[paper_id]
    #     db_operations.insert_paper(db_client, paper_id, title, abstract, None)

    #     # iterate through the references and citations for each paper
    #     for reference in references_and_citations[paper_id]['references']:
    #         db_operations.insert_reference(db_client, paper_id, reference)

    # # Iterate through the paper_ids and extract the paperId, title, and abstract
    # for paper_id in paper_ids:
    #     for citation in references_and_citations[paper_id]['citations']["data"]:
    #         db_operations.insert_paper(db_client, citation["citingPaper"]['paperId'], citation["citingPaper"]['title'], citation["citingPaper"]['abstract'], citation["citingPaper"]['url'])
    #         db_operations.insert_reference(db_client, citation["citingPaper"]['paperId'], paper_id)

    #     for reference in references_and_citations[paper_id]['references']["data"]:
    #         db_operations.insert_paper(db_client, reference["citedPaper"]['paperId'], reference["citedPaper"]['title'], reference["citedPaper"]['abstract'], reference["citedPaper"]['url'])
    #         db_operations.insert_reference(db_client, paper_id, reference["citedPaper"]['paperId'])

    def return_string_if_nonenull(input, input_name):
        if input is None:
            return "No " + input_name + " available"

    # Iterate through the paper_ids and extract the paperId, title, and abstract
    for paper_id in paper_ids:
        citations = references_and_citations[paper_id]['citations']
        if isinstance(citations, dict):
            citations = citations.get("data", [])

        for citation in citations:
            citing_paper = citation.get('citingPaper', {})
            paper_id_citing = citing_paper.get('paperId', 'unknown_id')
            title_citing = citing_paper.get('title', 'No Title')
            abstract_citing = return_string_if_nonenull(citing_paper.get('abstract', 'No abstract available'), "abstract")
            url_citing = citing_paper.get('url', None)

            if paper_id_citing and title_citing:
                db_operations.insert_paper(db_client, paper_id_citing, title_citing, abstract_citing, url_citing)
                db_operations.insert_reference(db_client, paper_id_citing, paper_id)
            else:
                logger.log_message(f"Skipping citing paper with missing required fields: {citing_paper}")
        
        
        references = references_and_citations[paper_id]['references']
        if isinstance(references, dict):
            references = references.get("data", [])

        for reference in references:
            cited_paper = reference.get('citedPaper', {})
            paper_id_cited = cited_paper.get('paperId', 'unknown_id')
            title_cited = cited_paper.get('title', 'No Title')
            abstract_cited = return_string_if_nonenull(cited_paper.get('abstract', 'No abstract available'), "abstract")
            url_cited = cited_paper.get('url', None)

            if paper_id_cited and title_cited:
                db_operations.insert_paper(db_client, paper_id_cited, title_cited, abstract_cited, url_cited)
                db_operations.insert_reference(db_client, paper_id, paper_id_cited)
            else:
                logger.log_message(f"Skipping cited paper with missing required fields: {cited_paper}")


        # Update is_processed to TRUE after processing
        try:
            db_operations.update_is_processed(db_client, paper_id)
        except Exception as e:
            logger.log_message(f"An error occurred while updating is_processed for paper {paper_id}. Start paper: {start_paper}, end paper: {end_paper}. Error: {e}")  
        
        # Add a wait time between processing each paper to avoid rate limiting
        time.sleep(1) 

    # Record the last successful trial
    logger.log_message(f"Last successful trial: Start Paper [{start_paper}], End Paper [{end_paper}], Date-Time [{time.ctime()}]")
    
    




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

    # db_operations.checked_for_references_and_citations(db_client) # to add a column to the papers table to check if the paper has been processed

    # =============================================
    # SEARCH AND SCRAPE
    # =============================================

    # Example usage
    start_page = 1
    end_page = 150
    search_terms = ["x", "x", "x"]
    
    # for search_term in search_terms:
    #     parsed_search_term = make_url_friendly(search_term)
    #     search_and_scrape(parsed_search_term, start_page, end_page, logger, db_client)

    # =============================================
    # SCRAPE REFERENCES
    # =============================================
    start_paper = 0
    end_paper = 4
    scrape_references_and_citations(logger, db_client, start_paper, end_paper)
    
    logger.close_log_file()

if __name__ == "__main__":
    main()
