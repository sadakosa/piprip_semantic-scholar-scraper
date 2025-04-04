import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from db import db_operations
import requests

import os
import json

from global_methods import load_checkpoint_references, save_checkpoint_references



# ====================================================================================================
# Crawler Class
# 
# This class contains the main logic for extracting the abstracts from the search results.
# Public Functions: 
# - close_cookie_banner: Closes the cookie banner if present
# - extract_title_and_ss_id: Extracts the title and Semantic Scholar ID from a search result
# - extract_abstract: Extracts the abstract from a search result
# - extract_references_and_citations: Extracts the references from a search result
# ====================================================================================================


class Crawler:
    def __init__(self, logger, db_client, db_read_client, driver=None):
        self.driver = driver
        self.logger = logger  
        self.db_client = db_client
        self.db_read_client = db_read_client

    def close_cookie_banner(self):
        try:
            cookie_banner = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.cookie-banner"))
            )
            accept_button = cookie_banner.find_element(By.TAG_NAME, "button")
            accept_button.click()
            time.sleep(2)  # Wait for the banner to close
        except Exception as e:
            print(f"Failed to close cookie banner: {e}")

    def extract_title_and_ss_id(self, result):
        title_elem = result.find('h2', class_='cl-paper-title')
        if title_elem:
            title = title_elem.text.strip() if title_elem.text else "No title available"
            ss_id = title_elem['id'].split("-", 1)[1] if 'id' in title_elem.attrs else "No ID available"
        else:
            title = "No title available"
            ss_id = "No ID available"
        
        return title, ss_id





















    # ====================================================================================================
    # Main Extract Abstract Function, and the corresponding private functions used below it. 
    # ====================================================================================================

    def extract_abstract(self, result, i, ss_id):
        print(f"Extracting abstract for result {i}...")

        # If there is an Expand Button, click it
        expand_buttons = result.find_all('button', class_='cl-button cl-button--no-arrow-divider cl-button--not-icon-only cl-button--no-icon cl-button--has-label cl-button--font-size- cl-button--icon-pos-left cl-button--shape-rectangle cl-button--size-default cl-button--type-tertiary cl-button--density-default more mod-clickable more-toggle')
        # logger.log_message(f"Expand buttons for result {i}: {expand_buttons}")
        # logger.log_message(f"Number of expand buttons for result {i}: {len(expand_buttons)}")
        
        if expand_buttons:
            expand_button = expand_buttons[0]
            button_id = f'expand_button_{i}'
            expand_button['id'] = button_id

            # Use JavaScript to set the ID attribute in the actual DOM
            self.__find_and_set_id_for_button(ss_id, button_id)
            button_clicked = self.__find_and_click_expand_button(button_id)
            
            # After clicking, reparse the HTML to get the updated content
            updated_soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        else:
            button_clicked = False

        if button_clicked:
            joined_text = self.__get_abstract_from_expanded_section(updated_soup)
            cleaned_text = self.__clean_abstract(joined_text)
            
            return cleaned_text
        else:
            # print(f"No Expand button found for result {i}")   
            return "No abstract available"
        


    def __find_and_set_id_for_button(self, ss_id, button_id):
        # JavaScript code to find the button based on the criteria and set its ID
        js_code = """
        var elements = document.getElementsByClassName('cl-button cl-button--no-arrow-divider cl-button--not-icon-only cl-button--no-icon cl-button--has-label cl-button--font-size- cl-button--icon-pos-left cl-button--shape-rectangle cl-button--size-default cl-button--type-tertiary cl-button--density-default more mod-clickable more-toggle');
        for (var i = 0; i < elements.length; i++) {
            var elem = elements[i];
            var parent = elem.parentElement;
            var found = false;
            for (var j = 0; j < 4; j++) {
                if (parent == null) break;
                if (parent.getAttribute('data-paper-id') == arguments[0]) {
                    found = true;
                    break;
                }
                parent = parent.parentElement;
            }
            if (found || (elem.parentElement != null && elem.parentElement.parentElement != null && elem.parentElement.parentElement.parentElement != null && elem.parentElement.parentElement.parentElement.getAttribute('data-paper-id') == arguments[0])) {
                elem.setAttribute('id', arguments[1]);
                elem.style.backgroundColor = 'yellow';
                return true;
            }
        }
        return false;
        """

        # Execute the JavaScript code
        found = self.driver.execute_script(js_code, ss_id, button_id)
        
        if found:
            return True
        else:
            return False


    def __find_and_click_expand_button(self, button_id):   
        try:
            selenium_button = self.driver.find_element(By.ID, button_id)
            # logger.log_message(f"Found and highlighted button with data-paper-id: {data_paper_id}")
        except Exception as e:
            # logger.log_message(f"Exception finding button by ID: {e}")
            return False
            
        # Scroll the button into view and click
        try:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", selenium_button)
            time.sleep(2)
            selenium_button.click()
        except Exception as e:
            self.logger.log_message(f"Exception clicking button: {e}")
            try:
                self.driver.execute_script("arguments[0].click();", selenium_button)
            except Exception as e2:
                self.logger.log_message(f"Exception clicking button with fallback JavaScript: {e2}")
                return False

        time.sleep(0.5)
        return True




    def __get_abstract_from_expanded_section(self, updated_soup):
        # Find all buttons with class "cl-button__label" containing "Collapse"
        collapse_buttons = updated_soup.find_all('span', class_='cl-button__label', string='Collapse')
        last_collapse_button = collapse_buttons[-1]
        parent_tag = last_collapse_button.parent
        previous_sibling = parent_tag.find_previous_sibling()

        if previous_sibling and previous_sibling.name == 'div': # when there is TLDR section, then it is a div tag
            span_elements = previous_sibling
        else: # when there is no TLDR section, then it is a span tag
            span_elements = parent_tag.parent

        joined_text = ''.join(span_element.get_text(strip=True) for span_element in span_elements)

        return joined_text
    
    def __clean_abstract(self, text):
        # Remove the "Abstract" at the start
        if text.startswith("Abstract"):
            text = text[len("Abstract"):].strip()
        
        # Remove the "Collapse" at the end
        if text.endswith("Collapse"):
            text = text[:-len("Collapse")].strip()
        
        return text    
    











    # ====================================================================================================
    # Main Extract References Function, and the corresponding private functions used below it. 
    # ====================================================================================================
    def process_paper(self, id, ss_id):
        # Placeholder for the actual processing logic
        # Replace this with actual implementation to retrieve references and citations
        references = []
        citations = []

        print(f"Extracting references and citations for paper {id}...")

        # citations
        try:
            url = f"https://api.semanticscholar.org/graph/v1/paper/{ss_id}/citations?fields=paperId,title,abstract,url"

            response = requests.get(url)
            # print(f"Response for paper {id}: {response}")

            if response.status_code == 200:
                citations = response.json()
            else:
                self.logger.log_message(f"An error occurred while extracting citations for paper {id} with ss_id {ss_id}. Error: {response.status_code}")
                raise Exception(f"Error: {response.status_code}, {response.text}")
        except Exception as e:
            self.logger.log_message(f"An error occurred while extracting citations for paper {id} with ss_id {ss_id}. Error: {e}")


        # references
        try:
            url = f"https://api.semanticscholar.org/graph/v1/paper/{ss_id}/references?fields=paperId,title,abstract,url"

            response = requests.get(url)

            if response.status_code == 200:
                references = response.json()
            else:
                self.logger.log_message(f"An error occurred while extracting references for paper {id} with ss_id {ss_id}. Error: {response.status_code}")
                raise Exception(f"Error: {response.status_code}, {response.text}")
        except Exception as e:
            self.logger.log_message(f"An error occurred while extracting references for paper {id} with ss_id {ss_id}. Error: {e}")


        
        return references, citations






    def extract_references_and_citations(self, search_term, previous_hop, start_paper, batch_size, checkpoint_file="checkpoint.json"):
        # retrieve papers from database
        # call the semantic scholar API for references and citations
        # iterate through the references and citations and insert them into the database

        paper_ids = db_operations.get_all_paper_ids_with_params(self.db_read_client, search_term, previous_hop)
        self.logger.log_message(f"Retrieved all paper IDs. Paper IDs: {paper_ids}.")
        print(f"Retrieved all paper IDs. Paper IDs: {paper_ids}.")


        checkpoint = load_checkpoint_references()
        if checkpoint is not None:
            print("there is checkpoint")
            collated_references_and_citations = checkpoint['collated_references_and_citations']
        else:
            print("no checkpoint")
            checkpoint = {
                'search_term': search_term,
                'previous_hop': previous_hop,
                'last_processed_paper': 0,
                'collated_references_and_citations': {}
            }
            collated_references_and_citations = {}

        retrieved_count = 0
        list_of_new_ids = []
        for idx, (id, ss_id, is_processed) in enumerate(paper_ids[start_paper:start_paper + batch_size], start=start_paper):
            # Process each paper
            if is_processed:
                # Save checkpoint as paper has been processed
                checkpoint["last_processed_paper"] = idx + start_paper
                checkpoint["collated_references_and_citations"] = collated_references_and_citations
                save_checkpoint_references(checkpoint)
            else:
                references, citations = self.process_paper(id, ss_id)  
            
                collated_references_and_citations[id] = {
                    'ss_id': ss_id,
                    'citations': citations,
                    'references': references
                }
                list_of_new_ids.append(id)
                # Save checkpoint after processing each paper
                # checkpoint["last_processed_paper"] = idx + start_paper
                # checkpoint["collated_references_and_citations"] = collated_references_and_citations
                # save_checkpoint_references(checkpoint)

            self.logger.log_message(f"Processed paper {id} with ss_id {ss_id}.")
            retrieved_count += 1

        return collated_references_and_citations, retrieved_count, list_of_new_ids








