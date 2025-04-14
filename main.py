from utils.book_scraper import *
from utils.category_scraper import *
import os

# CONSTANT VARIABLES
BASE_URL = "https://books.toscrape.com/"
ASSETS_BASE = "assets/"
IMAGES_BASE = os.path.join(ASSETS_BASE, "images")
CSV_BASE = os.path.join(ASSETS_BASE, "csv")

def main():
    csv_file_path = os.path.join(CSV_BASE, "book_data.csv")
    absolute_csv_path = os.path.abspath(csv_file_path)
    print(f"Saving CSV file to {absolute_csv_path}.")

    try:
        # Get categories dictionary
        categories = generate_categories_list(BASE_URL)
        if not categories:
            print("No categories found.")
            return
        else:
            print(f"Categories found: {', '.join(categories.keys())}")

        all_books_data = []  # accumulate book data

        # Loop over each category
        for category_name, category_url in categories.items():
            print(f"\nProcessing category: {category_name}")

            total_books, total_pages, book_urls = scrape_category(category_url)
            print(f"Found {total_books} books over {total_pages} pages in {category_name} category.")

            # Process each book URL in the category
            for index, book_url in enumerate(book_urls, 1):
                print(f"({index}/{total_books}) Scraping book: {book_url}")
                book_info = scrape_book(book_url)
                if book_info:
                    all_books_data.append(book_info)
                else:
                    print(f"  Failed to scrape book: {book_url}")

        # Isolate unique entries by UPC
        unique_books = {book["universal_product_code"]: book for book in all_books_data}
        unique_books_list = list(unique_books.values())

        # Write all scraped data at once
        write_csv(unique_books_list, csv_file_path)

    except Exception as e:
        print(f"An error occurred while processing the data: {e}")

if __name__ == "__main__":
    main()