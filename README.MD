
# Project Title: Sunshine-Reggae

## ⚠️ Important Notice

This project involves web scraping, a technique used to extract data from websites. While this framework is designed to facilitate data collection for legitimate research and development purposes, it's crucial to adhere to ethical guidelines and legal restrictions:

- **Respect robots.txt**: Always check and comply with the `robots.txt` file of the target website, which indicates the site's scraping policies.
- **Rate Limiting**: Implement rate limiting in your scraping logic to avoid overwhelming the website's server.
- **User-Agent String**: Use a meaningful user-agent string to identify your scraper. This transparency helps in avoiding misidentification as a malicious bot.
- **Data Use**: Ensure that the data collected is used ethically and complies with the website's terms of service and applicable laws, including copyright and privacy regulations.

## 🚀 Project Overview

This project provides a robust framework for web scraping, designed for efficiency and flexibility. It leverages Selenium for dynamic content handling, offering an integrated database for seamless data storage and management. Ideal for researchers, developers, and analysts, this framework supports various use cases from market research to academic studies.

## 📂  Project Structure

Below is the detailed project directory layout, including descriptions for each component:

- 📁 **attractions/**: Contains scripts for scraping specific tourist attractions.
- 📁 **Chromedriver/**: Holds the ChromeDriver executable required for Selenium to interact with the Chrome browser.
- 📁 **Database/**: Includes the SQLite database and ORM models for structured data storage.
  - 📄 `__init__.py`: Initializes the database package.
  - 📄 `database.py`: Defines the database schema and ORM models.
- 📄 **main.py**: The main entry point for the scraping scripts.
- 📄 **.gitignore**: Specifies intentionally untracked files to ignore.
- 📄 **README.MD**: Offers an overview of the project, setup instructions, and usage examples.
- 📄 **requirements.txt**: Lists all the Python package dependencies for the project.
- 📁 **Storage/**: A designated space for temporary data storage during scraping sessions.

## 📚 Detailed Dependencies

The `requirements.txt` file contains all necessary Python packages. Here's a brief overview of key dependencies:

- `selenium`: Provides tools for browser automation, crucial for dynamic content scraping.
- `beautifulsoup4`: Aids in HTML and XML parsing for easy data extraction.
- `requests`: Enables HTTP requests for fetching web pages.
- `SQLAlchemy`: Offers ORM capabilities for database interactions.
- `pandas`: Facilitates data analysis and manipulation.

## 🛠 Setup and Execution

- **Environment Preparation**: Ensure Python 3.8+ is installed. Clone the repository and navigate into the project directory.

- **Dependency Installation**: Run the command to install required packages.
  - pip install -r requirements.txt

- **Driver Setup**: Download the correct version of ChromeDriver matching your Chrome version and place it in the Chromedriver/ directory.

- **Database Initialization**: Run the following command to set up the database schema.
  - python Database/database.py

- **Running the Scraper**: Execute the following command to start scraping. Parameters and targets can be configured within this script.
  - python main.py

## 📝 Contribution Guidelines

We welcome contributions! Please refer to CONTRIBUTING.md for guidelines on how to submit issues, feature requests, and code.
