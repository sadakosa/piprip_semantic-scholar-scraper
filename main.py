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


def close_cookie_banner(driver):
    try:
        cookie_banner = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.cookie-banner"))
        )
        accept_button = cookie_banner.find_element(By.TAG_NAME, "button")
        accept_button.click()
        time.sleep(2)  # Wait for the banner to close
    except Exception as e:
        print(f"Failed to close cookie banner: {e}")

def extract_title_and_ss_id(result):
    title_elem = result.find('h2', class_='cl-paper-title')
    if title_elem:
        title = title_elem.text.strip() if title_elem.text else "No title available"
        ss_id = title_elem['id'].split("-", 1)[1] if 'id' in title_elem.attrs else "No ID available"
    else:
        title = "No title available"
        ss_id = "No ID available"
    
    return title, ss_id

def extract_abstract(result, driver, i):
    print(f"Extracting abstract for result {i}...")
    # Simulate clicking the "Expand" button to reveal the abstract
    expand_buttons = result.find_all('button', class_='cl-button cl-button--no-arrow-divider cl-button--not-icon-only cl-button--no-icon cl-button--has-label cl-button--font-size- cl-button--icon-pos-left cl-button--shape-rectangle cl-button--size-default cl-button--type-tertiary cl-button--density-default more mod-clickable more-toggle')

    expand_button = expand_buttons[0]
    if 'Expand' in expand_button.text:
        button_id = f'expand_button_{i}'
        expand_button['id'] = button_id

        # Extract the class names from the BeautifulSoup Tag
        class_names = expand_button['class']

        # Use JavaScript to set the ID attribute in the actual DOM
        class_name_string = " ".join(class_names)
        driver.execute_script(
            "document.getElementsByClassName(arguments[0])[arguments[1]].setAttribute('id', arguments[2]);",
            class_name_string, i, button_id
        )

        selenium_button = driver.find_element(By.ID, button_id)
        
        # Scroll the button into view and click
        driver.execute_script("arguments[0].scrollIntoView(true);", selenium_button)
        time.sleep(1)

        try:
            selenium_button.click()
        except Exception:
            driver.execute_script("arguments[0].click();", selenium_button)
        
        time.sleep(0.5)
        print(f"Clicked button_{i}")

        # After clicking, reparse the HTML to get the updated content
        updated_soup = BeautifulSoup(driver.page_source, 'html.parser')
        abstract_title_elements = updated_soup.find_all('div', class_='tldr-abstract__pill')
        abstract_title_element = abstract_title_elements[2 * i + 1] 
        print("abstract_title_element: ", abstract_title_element)
        if abstract_title_element:
            # Find all span elements after this div
            all_spans = abstract_title_element.find_all_next('span')
            # Check if there are at least two span elements
            if len(all_spans) > 1:
                # Get the second span element
                second_span_element = all_spans[1]
                
                # Extract and print the abstract text
                abstract_text = ''.join(second_span_element.stripped_strings)
                return abstract_text
            else:
                print("Less than two span elements found after the specified div.")
        else:
            abstract_text = "No abstract available"
            print("abstract: ", abstract_text)











def search_and_scrape(term, start_page, end_page, logger, db_client):
    # Setup WebDriver (e.g., ChromeDriver)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode for faster execution
    driver = webdriver.Chrome(options=options)
    driver.delete_cookie('IS_SELENIUM')

    base_url = "https://www.semanticscholar.org"
    search_url = f"{base_url}/search?fos%5B0%5D=computer-science&q={term}&sort=total-citations&page="
    
    for current_page in range(start_page, end_page + 1):
        try:
            # Open the search URL for the current page
            driver.get(search_url + str(current_page))

            # Wait for the search results to load (adjust the timeout as needed)
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "cl-paper-row"))
            )
            # Close the cookie banner if present
            close_cookie_banner(driver)
                
            # Adding delay to ensure the page has enough time to load
            time.sleep(5)

            # Get the page source and parse it with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Find the elements that contain the search results
            results = soup.find_all('div', class_='cl-paper-row')

            if not results:
                print(f"No results found on page {current_page}. Ending search.")
                break  # Exit the loop if no results are found (end of pages)
            
            # Extract and print the information from each result
            for i, result in enumerate(results):
                try:
                    title, ss_id = extract_title_and_ss_id(result)
                    abstract = extract_abstract(result, driver, i)
                    print(f"Title: {title}\nPaper ID: {ss_id}\nAbstract: {abstract}")
                except AttributeError as e:
                    print(f"Error parsing result: {e}")

            # Record the last successful trial
            logger.log_message(f"Last successful trial: Current Page [{current_page}], Search Term [{term}], Date-Time [{time.ctime()}]")
            # Be polite and wait a bit before the next request to avoid being blocked
            time.sleep(1)        

        except Exception as e:
            print(f"An error occurred on page {current_page}: {e}")
            logger.log_message(f"Last successful trial: Current Page [{current_page}], Search Term [{term}]")
            break  # Optionally, you can choose to retry or skip this page
    
    driver.quit()

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
    # CODE PROPER
    # =============================================

    # Example usage
    start_page = 1
    end_page = 2
    search_term = "information retrieval"
    parsed_search_term = make_url_friendly(search_term)
    search_and_scrape(parsed_search_term, start_page, end_page, logger, db_client)
    
    logger.close_log_file()

if __name__ == "__main__":
    main()
