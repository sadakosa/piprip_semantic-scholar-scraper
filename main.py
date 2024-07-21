import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import logging

from logger.logger import Logger
from db.db_client import DBClient
from global_methods import load_yaml_config, make_url_friendly, undo_url_friendly, get_search_terms
from global_methods import load_checkpoint_scrape, save_checkpoint_scrape, remove_checkpoint_scrape 
from global_methods import load_checkpoint_references, save_checkpoint_references, remove_checkpoint_references
from db import db_operations

# from random_1 import extract_abstract_test
from crawler import Crawler

import json
import os










# ====================================================================================================
# First Scrapping Method - Search and Scrape
# ====================================================================================================

def search_and_scrape(term, start_page, end_page, logger, db_client):

    # Load the checkpoint if it exists
    # checkpoint = load_checkpoint_scrape()
    # if checkpoint:
    #     start_page = checkpoint['current_page']
    #     term = checkpoint['search_term']
        
    checkpoint = load_checkpoint_scrape()
    if checkpoint and checkpoint['search_term'] == term:
        start_page = checkpoint['current_page']
        last_processed_item = checkpoint['last_processed_item']
        logger.log_message(f"Resuming search from page {start_page} for search term {term}")
    else:
        last_processed_item = -1


    # Setup WebDriver (e.g., ChromeDriver)
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    # options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--remote-debugging-port=9222")
    # options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-breakpad")
    options.add_argument("--disable-client-side-phishing-detection")
    options.add_argument("--disable-default-apps")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-features=Translate")
    options.add_argument("--disable-hang-monitor")
    options.add_argument("--disable-ipc-flooding-protection")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--disable-prompt-on-repost")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-sync")
    options.add_argument("--force-color-profile=srgb")
    options.add_argument("--metrics-recording-only")
    options.add_argument("--no-first-run")
    options.add_argument("--password-store=basic")
    options.add_argument("--use-mock-keychain")
    options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(options=options)

    
    driver.delete_all_cookies()
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
                    db_operations.insert_paper(db_client, ss_id, title, abstract, paper_url, undo_url_friendly(term), 0)
                    # print(f"Title: {title}\nPaper ID: {ss_id}\nAbstract: {abstract}")
                except AttributeError as e:
                    # print(f"Error parsing result: {e}")
                    logger.log_message(f"Error parsing result for result {i} on page {current_page}, search term {term}. Error: {e}")
                
                # Save the checkpoint after processing each item
                save_checkpoint_scrape(term, current_page, i)

            # Record the last successful trial
            logger.log_message(f"Last successful trial: Current Page [{current_page}], Search Term [{term}], Date-Time [{time.ctime()}]")
            # Be polite and wait a bit before the next request to avoid being blocked
            time.sleep(1)        

        except Exception as e:
            # print(f"An error occurred on page {current_page}: {e}")
            logger.log_message(f"An error occurred on page {current_page} for search term {term}. Error: {e}")
            logger.log_message(f"Last successful trial: Current Page [{current_page}], Search Term [{term}]")
            continue  # Optionally, you can choose to retry or skip this page
    
    driver.quit()

    # Remove the checkpoint file after successful completion
    remove_checkpoint_scrape()









# ====================================================================================================
# Second Scrapping Method - Scrape References & Citations
# ====================================================================================================

def scrape_references_and_citations(logger, db_client, db_read_client, search_term, previous_hop):
    crawler = Crawler(logger, db_client, db_read_client)

    checkpoint = load_checkpoint_references()
    if checkpoint and 'last_processed_paper' in checkpoint:
        start_paper = int(checkpoint['last_processed_paper'])
    else:
        checkpoint = {
            'search_term': search_term,
            'previous_hop': previous_hop,
            'last_processed_paper': 0,
            'collated_references_and_citations': {}
        }
        start_paper = 0

    while True:
        logger.log_message("retrieving papers from: " + str(start_paper))
        references_and_citations, retrieved_count, list_of_new_ids = crawler.extract_references_and_citations(
            search_term, previous_hop, start_paper, batch_size=200
        )

        if not retrieved_count:
            logger.log_message("done with retrieving papers")
            break  # Exit loop if no papers were processed in this batch
        
        logger.log_message("inserting references and citations for papers: " + str(start_paper) + " - " + str(start_paper + retrieved_count - 1))
        insert_references_and_citations(logger, db_client, references_and_citations, search_term, previous_hop, list_of_new_ids)

        checkpoint['last_processed_paper'] = start_paper + retrieved_count
        checkpoint['collated_references_and_citations'].update(references_and_citations)
        save_checkpoint_references(checkpoint)

        start_paper += retrieved_count

    references_and_citations_string = json.dumps(checkpoint['collated_references_and_citations'])
    # print("References and Citations: ", references_and_citations_string)
    logger.log_message(f"References and Citations: {references_and_citations_string}")

    # Log the last successful trial
    logger.log_message(f"Last successful trial: Search Term [{search_term}], Previous Hop [{previous_hop}], Last Retrieved Paper [{start_paper}], Date-Time [{time.ctime()}]")
    remove_checkpoint_references()

def insert_references_and_citations(logger, db_client, references_and_citations, search_term, previous_hop, list_of_new_ids):
    def return_string_if_nonenull(value, key):
        return value if value else f"No {key} available"
        
    # Iterate through the paper_ids and extract the paperId, title, and abstract
    for id in list_of_new_ids:
        print(f"Processing paper: {id}")
        ss_id = references_and_citations[id]['ss_id']

        citations = references_and_citations[id]['citations']
        if isinstance(citations, dict):
            citations = citations.get("data", [])

        for citation in citations:
            citing_paper = citation.get('citingPaper', {})
            ss_id_citing = citing_paper.get('paperId', 'unknown_id')
            title_citing = citing_paper.get('title', 'No Title')
            abstract_citing = return_string_if_nonenull(citing_paper.get('abstract', 'No abstract available'), "abstract")
            url_citing = citing_paper.get('url', None)

            if ss_id_citing and title_citing:
                # print(f"Inserting citing paper: {abstract_citing}")
                db_operations.insert_paper(db_client, ss_id_citing, title_citing, abstract_citing, url_citing, search_term, previous_hop + 1)
                db_operations.insert_reference(db_client, ss_id_citing, ss_id)
            else:
                logger.log_message(f"Skipping citing paper with missing required fields: {citing_paper}")
        
        
        references = references_and_citations[id]['references']
        if isinstance(references, dict):
            references = references.get("data", [])

        for reference in references:
            # print(f"Processing reference: {reference}")
            cited_paper = reference.get('citedPaper', {})
            paper_id_cited = cited_paper.get('paperId', 'unknown_id')
            title_cited = cited_paper.get('title', 'No Title')
            abstract_cited = return_string_if_nonenull(cited_paper.get('abstract', 'No abstract available'), "abstract")
            url_cited = cited_paper.get('url', None)

            if paper_id_cited and title_cited:
                db_operations.insert_paper(db_client, paper_id_cited, title_cited, abstract_cited, url_cited, search_term, previous_hop + 1)
                db_operations.insert_reference(db_client, ss_id, paper_id_cited)
            else:
                logger.log_message(f"Skipping cited paper with missing required fields: {cited_paper}")

        # Update is_processed to TRUE after processing
        try:
            db_operations.update_is_processed(db_client, ss_id)
        except Exception as e:
            logger.log_message(f"An error occurred while updating is_processed for paper {id}, {ss_id}. search_term: {search_term}, previous_hops: {previous_hop}. Error: {e}")  

        # Add a wait time between processing each paper to avoid rate limiting
        time.sleep(1) 




    





# ====================================================================================================
# MAIN FUNCTION
# ====================================================================================================

def main():
    logger = Logger() # To log last try

    # =============================================
    # POSTGRESQL DATABASE CONNECTION
    # =============================================

    config = load_yaml_config('config/config.yaml')
    rds_db = config['RDS_DB']
    
    # PostgreSQL database connection details
    psql_user = config['PSQL_USER'] if rds_db else config['LOCAL_PSQL_USER']
    psql_password = config['PSQL_PASSWORD'] if rds_db else config['LOCAL_PSQL_PASSWORD']
    psql_host = config['PSQL_HOST'] if rds_db else config['LOCAL_PSQL_HOST']
    psql_port = config['PSQL_PORT'] if rds_db else config['LOCAL_PSQL_PORT']
    psql_read_host = config['PSQL_READ_HOST'] if rds_db else config['LOCAL_PSQL_HOST']

    db_client = DBClient("postgres", psql_user, psql_password, psql_host, psql_port)
    db_read_client = DBClient("postgres", psql_user, psql_password, psql_read_host, psql_port)

    # Set up the database schema
    # db_operations.create_paper_table(db_client)
    # db_operations.create_references_table(db_client)

    # =============================================
    # SEARCH TERMS SETTINGS
    # =============================================

    search_terms = get_search_terms() # there are 460 search terms in total
    start_term = 0
    end_term = 6

    # =============================================
    # SEARCH AND SCRAPE
    # =============================================

    # Example usage
    start_page = 1
    end_page = 101

    # for i in range(start_term, end_term + 1):
    #     search_term = search_terms[i][0]
    #     parsed_search_term = make_url_friendly(search_term)
    #     search_and_scrape(parsed_search_term, start_page, end_page, logger, db_client)

    # =============================================
    # SCRAPE REFERENCES
    # =============================================
    start_paper = 100
    end_paper = 102
    previous_hop = 0

    for i in range(start_term, end_term + 1):
        search_term = search_terms[i][0]
        logger.log_message(f"Processing search term: {search_term}")
        scrape_references_and_citations(logger, db_client, db_read_client, search_term, previous_hop)
    
    logger.close_log_file()

if __name__ == "__main__":
    main()
