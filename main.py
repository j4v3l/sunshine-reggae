"""
    Scrape the Visit X website to extract information about attractions 
    and save it to a database.
    The code uses the `selenium` library to scrape the website and the `requests` library 
    to download images.
    The `Database` module is used to save the scraped data to a SQLite database.
    The `sanitize_filename` function is used to create a valid filename 
    for the images by removing or replacing characters that are not allowed in filenames.
    The `setup_webdriver` function is used to set up the Chrome WebDriver for headless browsing.
    The `wait_for_images` function waits for images to load on the page.
    The `open_detail_page_and_extract_info` function opens the detail page 
    of an attraction and extracts additional information such as 
    address, phone, description, and image.
    The `convert_image_to_blob` function reads the image file and returns the image data as a blob.
    The `download_image` function downloads the image and saves it,
    with a filename based on the attraction's title.
    The `scrape_attractions` function scrapes the Visit X website to extract information 
    about attractions and saves it to a database.
"""

import os
from Attractions.constants import IMAGE_DIR
import Database.database as database  # Make sure this matches the name of your database module
from Attractions.attractions import scrape_attractions

# Initialize the database (create tables if they don't exist)
database.initialize_db()

if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)


def main():
    """Scrape the Visit X website to extract information about attractions 
    and save it to a database."""
    url = os.getenv("SCRAPING_URL")
    if not url:
        raise ValueError("SCRAPING_URL environment variable is not set.")
    scrape_attractions(url)


if __name__ == "__main__":
    main()
