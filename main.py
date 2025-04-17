from utils.book_scraper import scrape_book, write_csv, download_book_images
from utils.category_scraper import generate_categories_list, scrape_category
import os
import csv # to process the csv file
import requests # to make requests to image_urls for download
from urllib.parse import urlparse # to extract image url paths

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
        download_book_images_from_csv(csv_file_path)


    except Exception as e:
        print(f"An error occurred while processing the data: {e}")

# Once CSV file is written, it can be processed for downloading image_urls
def download_book_images_from_csv(csv_file_path):
    """
    Inputs the generated csv file, reads it for image_urls to download the book images for each book
    Outputs each downloaded image file as a .jpg file in /assets/images directory
    """
    # 1. Set the directory where images should be saved: "assets/images/"
    image_dir = os.path.join("assets", "images")

    # 2. If the directory doesn't exist, create it using os.makedirs()
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
        print(f"Created image directory at: {image_dir}")
    else:
        print("Directory already exists.")

    # 3. Open the CSV file using csv.DictReader() obtain the image_urls from each row
    try:
        with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
            reader = list(csv.DictReader(csvfile)) # converts to a list
            image_urls = [row["image_url"] for row in reader if "image_url" in row and row["image_url"]]
            print(f"Loaded {len(image_urls)} image URLs from CSV.")
            # 4. Count the total number of rows (images to download) and compare to total retreived image_urls
            if not image_urls:
                print("No image URLs found.")
            elif len(image_urls) < len(reader):
                print(f"Warning: {len(reader) - len(image_urls)} entries are missing image URLs.")
                missing_images = [row for row in reader if not row.get("image_url")]
                for index, row in enumerate(missing_images, 1):
                    print(f"Missing image URL for book entry #{index}: {row.get('title', 'Unknown Title')}")
            else:
                print("All book entries have image URLs.")

    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    # 5. Loop through each row with enumerate():
    #     a. Extract 'image_url' from the current row
    #     b. If no image_url, print a message and continue to next
    #     c. Use urlparse + os.path.basename() to extract filename from the URL
    #     d. Construct full local file path: os.path.join(image_dir, filename)
    #     e. Check if the image already exists at that location
    #        - If so, print a "already exists" message and continue
    #     f. Download the image using requests.get(url, stream=True)
    #        - If status_code == 200:
    #            - Open the local file in 'wb' mode
    #            - Write to file in chunks (iter_content)
    #            - Print a progress message
    #        - Else:
    #            - Print a failure message
    #     g. Catch and print any exceptions raised during download

if __name__ == "__main__":
    main()