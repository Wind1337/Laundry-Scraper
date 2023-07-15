from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from collections import Counter
from datetime import datetime
import re
import sys


def get_status(section):
    title_elem = section.find_element(By.CSS_SELECTOR, 'div.accordion__title')
    parent_div_class = title_elem.get_attribute('class')

    # Determine the status based on the parent div class
    if 'accordion__title--idle' in parent_div_class:
        status = 'Cycle Complete'
    elif 'accordion__title--in-use' in parent_div_class:
        status = 'In Use'
    elif 'accordion__title--dryer' in parent_div_class:
        status = 'Dryer Available'
    elif 'accordion__title' in parent_div_class:
        status = 'Washer Available'
    else:
        status = 'Unknown'

    return status


def clean_contents(p_tag, duration=None):
    p_contents = p_tag.get_attribute('innerHTML')

    # Remove HTML tags and links using regular expressions
    p_contents = re.sub('<.*?>', '', p_contents)
    p_contents = p_contents.replace('Report a fault', '')

    # If duration is not None, remove it from the text
    if duration:
        p_contents = p_contents.replace(duration, '', 1)

    # Remove invisible line breaks but maintain line breaks between sentences
    p_contents = p_contents.replace('<br>', '').replace('</small>', '</small>\n')

    return p_contents.strip()


def process_sections(driver, sections):
    status_counter = Counter()
    completion_times = []

    # Loop through each section and extract the information
    for section in sections:
        title = section.find_element(By.CSS_SELECTOR, 'div.accordion__title').text
        status = get_status(section)

        # Increment the counter for the status
        status_counter[status] += 1

        # If in use, extract duration
        duration = None
        if status == 'In Use':
            span_tags = section.find_elements(By.CSS_SELECTOR, 'p span')

            # Loop through the <span> tags and find the one containing "mins"
            for span_tag in span_tags:
                text = driver.execute_script("return arguments[0].textContent;", span_tag)
                if 'mins' in text:
                    duration = text.strip()
                    break

        p_contents = clean_contents(section.find_element(By.CSS_SELECTOR, 'p'), duration)

        # Extract expected completion time
        if 'Expected completion time' in p_contents:
            match = re.search(r'\d{2}:\d{2}', p_contents)
            if match:
                completion_time = datetime.strptime(match.group(), '%H:%M').time()
                completion_times.append(completion_time)

        print(f"\n{title}, Status: {status}")
        print(p_contents)
        if duration:
            print(f"Duration: {duration}")

    return status_counter, completion_times


class LaundryScraper:
    def __init__(self, site_url, chromedriver_path=None, debug=0):
        self.debug = debug
        self.site_url = site_url

        # Set up Chrome options
        chrome_options = Options()
        if debug == 0:
            chrome_options.add_argument("--headless")  # Run Chrome in headless mode
            chrome_options.add_argument("--disable-gpu")  # Disable GPU acceleration

        if chromedriver_path:
            # Set up the Selenium web driver
            service = Service(chromedriver_path)

            # Create a new Chrome driver instance
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
        else:
            self.driver = webdriver.Chrome(options=chrome_options)

    def scrape(self):
        print("Starting scraping")

        # Open the target website
        self.driver.get(self.site_url)

        try:
            # Find all the washer sections
            washer_sections = self.driver.find_elements(By.CSS_SELECTOR,
                                                        'section.accordions--circuit-view:nth-of-type(1) div.accordion')

            washer_status_counter, washer_completion_times = process_sections(self.driver, washer_sections)

            # Click on the anchor tag with text "View Dryers"
            dryers_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//a[contains(text(), "View Dryers")]'))
            )
            dryers_button.click()

            # Find all the dryer sections
            dryer_sections = self.driver.find_elements(By.CSS_SELECTOR,
                                                       'section.accordions--circuit-view:nth-of-type(2) div.accordion')

            dryer_status_counter, dryer_completion_times = process_sections(self.driver, dryer_sections)

            # Print the washer status counts
            print("\nWasher Status Counts:")
            for status, count in washer_status_counter.items():
                print(f"{status}: {count}")

            # Print the dryer status counts
            print("\nDryer Status Counts:")
            for status, count in dryer_status_counter.items():
                print(f"{status}: {count}")

            # Check if "Washer Available" or "Dryer Available" is present
            if 'Washer Available' not in washer_status_counter:
                # Print the earliest expected completion time
                if washer_completion_times:
                    earliest_completion_time = min(washer_completion_times)
                    print(f"\nEarliest Expected Washer Completion Time: {earliest_completion_time.strftime('%H:%M')}")

            if 'Dryer Available' not in dryer_status_counter:
                # Print the earliest expected completion time
                if dryer_completion_times:
                    earliest_completion_time = min(dryer_completion_times)
                    print(f"\nEarliest Expected Dryer Completion Time: {earliest_completion_time.strftime('%H:%M')}")

        finally:
            # Close the browser
            self.driver.quit()


if __name__ == "__main__":
    # Check if running on Android
    is_android = hasattr(sys, 'getandroidapilevel')

    laundry_rooms = {
        1: ["Murano Street Csb Laundry", "https://www.circuit.co.uk/circuit-view/laundry-site/?site=6240"],
        2: ["Murano Street Cheviot Laundry", "https://www.circuit.co.uk/circuit-view/laundry-site/?site=6239"]
    }

    print('Laundry Scrapper')
    print('Supported Laundry Rooms:')
    for key, value in laundry_rooms.items():
        print(key, ':', value[0])
    option = int(input('Select an option: '))

    if option not in laundry_rooms:
        print('Invalid selection')
        sys.exit(1)

    # Instantiate and run the scraper
    if is_android:
        scraper = LaundryScraper(laundry_rooms[option][1])
    else:
        scraper = LaundryScraper(laundry_rooms[option][1], "./")
    scraper.scrape()
