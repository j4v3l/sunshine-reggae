import sqlite3
from contextlib import contextmanager

DATABASE_PATH = "./Storage/attractions.db"


@contextmanager
def get_db_connection():
    """ Get a database connection

    Yields:
        _type_: sqlite3.Connection
    """
    conn = sqlite3.connect(DATABASE_PATH)
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def get_db_cursor(commit=False):
    """ Get a database cursor
    Args:
        commit (bool): Whether to commit the transaction

    Yields:
        _type_: sqlite3.Cursor
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        try:
            yield cursor
            if commit:
                conn.commit()
        finally:
            cursor.close()


def initialize_db():
    """Initialize the database by creating the 'attractions' table if it doesn't exist."""
    with get_db_cursor(commit=True) as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attractions (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                location TEXT NOT NULL,
                image BLOB,
                detail_link TEXT UNIQUE,
                page INTEGER,
                address TEXT,
                phone TEXT,
                description TEXT
            );
            """)


def save_attraction(attraction, image_blob):
    """ 
        Save an attraction to the database

    """
    with get_db_cursor(commit=True) as cursor:
        cursor.execute(
            "SELECT id FROM attractions WHERE detail_link = ?",
            (attraction["detail_link"], ),
        )
        exists = cursor.fetchone()
        if not exists:
            cursor.execute(
                """
                INSERT INTO attractions (title, location, image, detail_link, page, address, phone, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    attraction["title"],
                    attraction["location"],
                    image_blob,  # Save the image as a BLOB
                    attraction["detail_link"],
                    attraction["page"],
                    attraction.get("additional_info", {}).get("address", ""),
                    attraction.get("additional_info", {}).get("phone", ""),
                    attraction.get("additional_info", {}).get(
                        "description", ""),
                ),
            )
        else:
            print(
                f"Record with detail_link '{attraction['detail_link']}' already exists. Skipping insertion."
            )


def get_last_scraped_page():
    """ Get the last page number that was scraped

    Returns:
        _type_: int
    """
    with get_db_cursor() as cursor:
        cursor.execute("SELECT MAX(page) FROM attractions")
        result = cursor.fetchone()[0]
        return result if result is not None else 0
