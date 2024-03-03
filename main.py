"""
    Scrape the Visit Jamaica website to extract information about attractions and save it to a database.
    The code uses the `selenium` library to scrape the website and the `requests` library to download images.
    The `Database` module is used to save the scraped data to a SQLite database.
    The `sanitize_filename` function is used to create a valid filename for the images by removing or replacing characters that are not allowed in filenames.
    The `setup_webdriver` function is used to set up the Chrome WebDriver for headless browsing.
    The `wait_for_images` function waits for images to load on the page.
    The `open_detail_page_and_extract_info` function opens the detail page of an attraction and extracts additional information such as address, phone, description, and image.
    The `convert_image_to_blob` function reads the image file and returns the image data as a blob.
    The `download_image` function downloads the image and saves it with a filename based on the attraction's title.
    The `scrape_attractions` function scrapes the Visit Jamaica website to extract information about attractions and saves it to a database.
"""

import os
import re
from time import sleep
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
import Database.database as database  # Make sure this matches the name of your database module

# Initialize the database (create tables if they don't exist)
database.initialize_db()

IMAGE_DIR = "./Storage/downloaded_images"
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)


def sanitize_filename(title):
    """
    Sanitize the title to create a valid filename by removing or replacing characters
    that are not allowed in filenames.
    """
    sanitized_title = re.sub(
        r'[<>:"/\\|?*]', "_",
        title)  # Replace invalid characters with underscores
    sanitized_title = re.sub(
        r"\s+", "_", sanitized_title)  # Replace spaces with underscores
    return sanitized_title


def setup_webdriver():
    """Set up the Chrome WebDriver for headless browsing.

    Returns:
        WebDriver: The WebDriver instance
    """
    CHROMEDRIVER_PATH = os.getenv("CHROMEDRIVER_PATH")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    service = Service(executable_path=CHROMEDRIVER_PATH)
    return webdriver.Chrome(service=service, options=chrome_options)


def wait_for_images(driver, timeout=10):
    """Wait for images to load on the page.

    Args:
        driver (WebDriver): The WebDriver instance
        timeout (int, optional): The maximum time to wait. Defaults to 10.
    """
    WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "img")))


def open_detail_page_and_extract_info(driver, url, title):
    """Open the detail page of an attraction and extract additional information such as address, phone, description, and image.

    Args:
        driver (WebDriver): The WebDriver instance
        url (_type_): The URL of the detail page
        title (_type_): The title of the attraction

    Returns:
        _type_: A dictionary containing the extracted information
    """
    driver.get(url)
    wait_for_images(driver)

    details = {
        "address": "Information not available",
        "phone": "Information not available",
        "description": "Information not available",
        "image_blob": None,  # Placeholder for the image blob
    }

    try:
        address_element = driver.find_element(By.CSS_SELECTOR,
                                              ".street-address")
        city_state_zip_element = driver.find_element(By.CSS_SELECTOR,
                                                     ".city-state-zip")
        details[
            "address"] = f"{address_element.text}, {city_state_zip_element.text}"
    except NoSuchElementException:
        print("Address information not available.")

    try:
        phone_element = driver.find_element(By.CSS_SELECTOR, "a[href^='tel:']")
        details["phone"] = phone_element.text
    except NoSuchElementException:
        print("Phone information not available.")

    try:
        description_element = driver.find_element(
            By.CSS_SELECTOR, "#descriptionTab .core-styles")
        details["description"] = description_element.text
    except NoSuchElementException:
        print("Description information not available.")

    # Extracting the image from the <img> tag with class "slide-img loaded"
    try:
        img_element = driver.find_element(By.CSS_SELECTOR,
                                          "img.slide-img.loaded")
        image_url = img_element.get_attribute("src")
        if image_url:
            # Correctly call download_image with title
            image_filename = download_image(image_url, title)
            if image_filename:
                # Ensure convert_image_to_blob is called correctly
                details["image_blob"] = convert_image_to_blob(image_filename)
            else:
                print("Failed to download the image.")
    except NoSuchElementException:
        print("Image element not found.")
    return details


def convert_image_to_blob(image_filename):
    """Read the image file and return the image data as a blob.

    Args:
        image_filename (_type_): The filename of the image

    Returns:
        _type_: The image data as a blob
    """
    with open(image_filename, "rb") as file:
        blob_data = file.read()
    return blob_data


def download_image(image_url, title):
    """
    Download the image and save it with a filename based on the attraction's title.
    """
    try:
        response = requests.get(image_url, timeout=10)
        if response.status_code == 200:
            sanitized_title = sanitize_filename(title)
            # Use the first 50 characters of the sanitized title to keep the filename length reasonable
            image_filename = os.path.join(IMAGE_DIR,
                                          f"{sanitized_title[:50]}.jpg")
            with open(image_filename, "wb") as file:
                file.write(response.content)
            return image_filename
        else:
            print(
                f"Failed to download image. Status code: {response.status_code}"
            )
    except requests.RequestException as e:
        print(f"Error downloading image: {e}")
    return None


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


def main():
    """Scrape the Visit Jamaica website to extract information about attractions and save it to a database."""
    url = os.getenv("SCRAPING_URL")
    scrape_attractions(url)
    attractions = scrape_attractions(url)
    print("Attractions Details:\n")
    print(json.dumps(attractions, indent=4, ensure_ascii=False))


if __name__ == "__main__":
    main()
