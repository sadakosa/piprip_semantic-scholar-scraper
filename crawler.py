import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# ====================================================================================================
# Crawler Class
# 
# This class contains the main logic for extracting the abstracts from the search results.
# Public Functions: 
# - close_cookie_banner: Closes the cookie banner if present
# - extract_title_and_ss_id: Extracts the title and Semantic Scholar ID from a search result
# - extract_abstract: Extracts the abstract from a search result
# ====================================================================================================


class Crawler:
    def __init__(self, driver, logger):
        self.driver = driver
        self.logger = logger  


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