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
    ## Possible to remove now ?
    book_relative_url = "catalogue/the-past-never-ends_942/index.html"
    url = urljoin(BASE_URL, book_relative_url)

    # Create a dictionary of book_info from extracted (scraped) data
    book_info = scrape_book(url)
    if not book_info:
        print(f"Scraping failed. Exiting program")
        return

    # Define CSV file path for writing
    ## Possible to remove now ?
    csv_file_path = os.path.join(CSV_BASE, "book_data.csv")
    abs_csv_path = os.path.abspath(csv_file_path)
    print(f"Saving csv file to {abs_csv_path}")

    # Obtain Image URL of book for download
    image_url = book_info["image_url"]

    try:
        # Write the scraped data to CSV path
        ## Possible to remove now ?
        write_csv(book_info, file_path=csv_file_path)

        # Download image to defined path
        ## Possible to remove now ?
        download_image(image_url, assets_folder=IMAGES_BASE)

        # Create a categories dictionary from category_scraper.py
        # - Keys are the category labels
        # - Values are the urls of the category pages from this list
        categories = generate_categories_list(BASE_URL)
        if not categories:
            print("No categories found.")
            return

        for category_name, category_url in categories.items():
            print(f"Processing category: {category_name}")
            total_books, total_pages, book_urls = scrape_category(category_url)
            print(f"You have found {total_books} books on {total_pages} page(s) in {category_name} category.")

            for book_url in book_urls:
                print(f"Scraping book: {book_url}")
                book_info = scrape_book(book_url)
                if book_info:
                    write_csv(book_info, file_path=csv_file_path)
                    download_image(book_info["image_url"], assets_folder=IMAGES_BASE)
                else:
                    print(f"Failed to scan the book in {book_url}")
            print(f"You have processed all (${total_books}) books .")

    except Exception as e:
        print(f"An error occurred while processing the data")

if __name__ == "__main__":
    main()