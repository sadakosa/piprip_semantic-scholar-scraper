import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from logger.logger import Logger


def search_and_scrape(term, start_page, end_page, logger):
    # Setup WebDriver (e.g., ChromeDriver)
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode for faster execution
    driver = webdriver.Chrome(options=options)

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

            # Print the HTTP response details
            logger.log_message(f"Text: {driver.page_source}\n")

            # Get the page source and parse it with BeautifulSoup
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Find the elements that contain the search results
            results = soup.find_all('div', class_='cl-paper-row')

            if not results:
                print(f"No results found on page {current_page}. Ending search.")
                break  # Exit the loop if no results are found (end of pages)

            # Extract and print the information from each result
            for result in results:
                try:
                    # title
                    title_elem = result.find('h2', class_='cl-paper-title')
                    title = title_elem.text.strip() if title_elem else "No title available"
                    print("title: ", title)
                    print("id: ", title_elem.get('id'))
                    # if title_elem else "No ID available"

                    paper_id = title_elem['id'] if title_elem and 'id' in title_elem.attrs else "No ID available"
                    
                    # Extract authors
                    # authors_elems = result.find_all('span', {'data-test-id': 'author-list'})
                    # authors = [author.find('span').text.strip() for author in authors_elems]
                    
                    # Simulate clicking the "Expand" button to reveal the abstract
                    expand_button = result.find('button', class_='cl-paper-abstract__btn')
                    if expand_button:
                        expand_button_id = expand_button['id']
                        driver.find_element(By.ID, expand_button_id).click()
                        time.sleep(0.5)  # Wait for the abstract to be revealed

                        # Get the updated page source after clicking "Expand"
                        updated_soup = BeautifulSoup(driver.page_source, 'html.parser')
                        updated_result = updated_soup.find('div', id=result['id'])
                        abstract_elem = updated_result.find('span', class_='cl-paper-abstract') if updated_result else None
                        abstract = abstract_elem.text.strip() if abstract_elem else "No abstract available"
                    else:
                        abstract = "No abstract available"

                    print(f"Title: {title}\nAuthors: {', '.join(authors)}\nAbstract: {abstract}\nLink: {link}\n")
                
                except AttributeError as e:
                    print(f"Error parsing result: {e}")

            # Be polite and wait a bit before the next request to avoid being blocked
            time.sleep(1)        

        except Exception as e:
            print(f"An error occurred on page {current_page}: {e}")
            logger.close_log_file()
            break  # Optionally, you can choose to retry or skip this page

    logger.close_log_file()
    driver.quit()

def main():
    logger = Logger()

    # Example usage
    start_page = 1
    end_page = 1
    search_term = "information%20retrieval"
    search_and_scrape(search_term, start_page, end_page, logger)

if __name__ == "__main__":
    main()
