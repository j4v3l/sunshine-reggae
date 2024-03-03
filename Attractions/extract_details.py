""" This module contains the functions to extract additional information from the detail page of an attraction.

    Returns:
        dict: A dictionary containing the extracted information
"""
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from Attractions.extract_images import download_image, wait_for_images


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
