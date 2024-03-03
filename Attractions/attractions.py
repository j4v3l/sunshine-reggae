"""
This module contains the functions to scrape the Visit Jamaica website to 
extract information about attractions and save it to a database.

    Returns:
        list: A list of dictionaries containing the extracted information
"""
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from Attractions.extract_details import open_detail_page_and_extract_info
from Attractions.setup import setup_webdriver
import Database.database as database


def scrape_attractions(url):
    """Scrape the Visit Jamaica website to extract information about attractions and save it to a database.

    Args:
        url (_type_): The URL of the attractions page

    Returns:
        _type_: A list of dictionaries containing the extracted information
    """
    driver = setup_webdriver()
    driver.get(url)
    sleep(5)  # Adjust based on page load time

    attractions = []
    start_page = database.get_last_scraped_page() + 1
    max_pages = 10  # Adjust as needed

    for page_count in range(start_page, start_page + max_pages):
        try:
            items = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "div.content.list div.item")))

            for item_index in range(len(items)):
                try:
                    item = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((
                            By.CSS_SELECTOR,
                            f"div.content.list div.item:nth-of-type({item_index + 1})",
                        )))
                    title = item.find_element(
                        By.CSS_SELECTOR,
                        "div.info div.top-info h4 a").text.strip()
                    location = item.find_element(By.CSS_SELECTOR,
                                                 "li.locations").text.strip()
                    image_src = item.find_element(
                        By.CSS_SELECTOR,
                        "div.image img.thumb").get_attribute("src")
                    detail_link_elements = item.find_elements(
                        By.CSS_SELECTOR, "div.info div.top-info h4 a")

                    if detail_link_elements:
                        detail_link = detail_link_elements[0].get_attribute(
                            "href")
                        detail_info = open_detail_page_and_extract_info(
                            driver, detail_link, title)
                        # Extract the image blob from detail_info
                        image_blob = detail_info.get("image_blob", None)
                        attraction = {
                            "page": page_count,
                            "title": title,
                            "location": location,
                            "image_src": image_src,
                            "detail_link":
                            detail_link,  # Ensure this key exists
                            "additional_info": detail_info,
                        }

                        database.save_attraction(attraction, image_blob)
                        print(f"Scraped: {title}")
                    else:
                        print(f"Detail link not found for item: {title}")

                    driver.back()
                    sleep(2)  # Adjust based on page load time

                except StaleElementReferenceException:
                    print("Encountered a stale element, retrying...")
                    continue  # Optionally, add logic to retry the operation

            page_count += 1
            if page_count > max_pages:
                break

            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "li.highlight a.nxt")))
            next_button.click()
            sleep(5)  # Adjust based on page load time

        except (NoSuchElementException, TimeoutException):
            print("No more pages to navigate.")
            break

    driver.quit()
    return attractions
