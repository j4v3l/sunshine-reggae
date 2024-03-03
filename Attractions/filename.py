""" This module contains the function to sanitize a title to create a valid filename.

    Returns:
        str: The sanitized title
"""
import re


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
