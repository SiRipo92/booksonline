from utils.book_scraper import *
from utils.category_scraper import *
import os
from urllib.parse import urljoin

# CONSTANT VARIABLES
BASE_URL = "https://books.toscrape.com/"
ASSETS_BASE = "assets/"
IMAGES_BASE = os.path.join(ASSETS_BASE, "images")
CSV_BASE = os.path.join(ASSETS_BASE, "csv")

def main():
    # Define url for book scraping
    book_relative_url = "catalogue/the-past-never-ends_942/index.html"
    url = urljoin(BASE_URL, book_relative_url)

    # Create a dictionary of book_info from extracted (scraped) data
    # book_info = scrape_book(url)
    # if not book_info:
        # print(f"Scraping failed. Exiting program")
        # return

    # Define CSV file path for writing
    ## Possible to remove now ?
    # csv_file_path = os.path.join(CSV_BASE, "book_data.csv")
    # abs_csv_path = os.path.abspath(csv_file_path)
    # print(f"Saving csv file to {abs_csv_path}")

    try:
        # Create a categories dictionary from category_scraper.py
        # - Keys are the category labels
        # - Values are the urls of the category pages from this list
        categories = generate_categories_list(BASE_URL)
        if not categories:
            print("No categories found.")
            return
        else:
            print(f"Categories found: {', '.join(categories)}")
        # Loop over category names and their urls
            # Scrape the category to obtain total_books, total_pages and book_urls to scan from category_url
            # Loop through book_urls retrieved from each category page url
            # For each book found w/ url, scrape that book url into a dictionary book_info
            # Write csv for each new entry
            # Download images from each image_url in each book page and set them in assets/images/ folder
            # If no book_info is found during scraping, print an error message
            # Else, when the loop finishes, print a message of success with information about the data collected

    except Exception as e:
        print(f"An error occurred while processing the data")

if __name__ == "__main__":
    main()