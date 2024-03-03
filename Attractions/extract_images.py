""" This module contains functions to download and convert images.

    Returns:
        _type_: The image data as a blob
"""
import os
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Attractions.constants import IMAGE_DIR
from Attractions.filename import sanitize_filename


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


def wait_for_images(driver, timeout=10):
    """Wait for images to load on the page.

    Args:
        driver (WebDriver): The WebDriver instance
        timeout (int, optional): The maximum time to wait. Defaults to 10.
    """
    WebDriverWait(driver, timeout).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "img")))
