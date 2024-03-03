"""This module sets up the Chrome WebDriver for headless browsing.

    Returns:
        WebDriver: The WebDriver instance
"""
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options


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
