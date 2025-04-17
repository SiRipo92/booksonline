from utils.book_scraper import scrape_book, write_csv, download_book_images
from utils.category_scraper import generate_categories_list, scrape_category
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
        # Step 1: Create a categories dictionary for category pages to scrape
        categories = generate_categories_list(BASE_URL)
        if not categories:
            print("No categories found.")
            return
        else:
            # Print a message displaying all the category names found
            print(f"Categories found: {', '.join(categories.keys())}")

        all_books_data = []  # Initializes a list to accumulate book_info dictionaries

        # Step 2: Loop over each category to extract total_books, total_pages, and book_urls
        # by scraping each category page url, then unpack each category page url and scrape it
        for category_name, category_url in categories.items():
            print(f"\nProcessing category: {category_name}")

            # Calls the function scrape_category with the given category_url and unpacks its return values:
            # total_books: the total number of books found in the category,
            # total_pages: the total number of pagination pages processed,
            # book_urls: a list of URLs for each individual book in the category.
            total_books, total_pages, book_urls = scrape_category(category_url)
            print(f"Found {total_books} books over {total_pages} page(s) in {category_name} category.")

            # Step 3: Process each book URL in the category pages
            # defaults index to 1/(total books)
            # Collect each individual book page url, scrape it and return output to book_info dictionary
            # As long as there is an index for books to scrape,
            # store each book_info dictionary in an all_books_data list
            for index, book_url in enumerate(book_urls, 1):
                print(f"({index}/{total_books}) Scraping book: {book_url}")
                book_info = scrape_book(book_url)
                if book_info:
                    all_books_data.append(book_info)
                else:
                    print(f"Failed to scrape book: {book_url}")

        # Step 4: Add a check to ensure no duplicate entries are scrapped and added
        # Creates a dictionary 'unique_books' that maps each book's unique UPC to the book_info dictionary,
        # effectively removing duplicate entries. Then, converts the dictionary values back
        # into a list of unique book_info dictionaries.
        unique_books = {book["universal_product_code"]: book for book in all_books_data}
        unique_books_list = list(unique_books.values())

        # Step 5: Write the unique_books_list into the csv folder
        write_csv(unique_books_list, csv_file_path)

        # Step 6: Download images and store them in /assets/images directory
        # download_book_images()


    except Exception as e:
        print(f"An error occurred while processing the data: {e}")

if __name__ == "__main__":
    main()