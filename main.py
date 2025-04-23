from utils.book_scraper import scrape_book, write_book_data_csv
from utils.category_scraper import (
    generate_categories_list,
    scrape_category,
    write_category_csv_files,
    merge_category_csvs, # <-- NEW: import fallback helper
)
import os
import csv # to process the csv file
import requests # to make requests to image_urls for download
from urllib.parse import urlparse # to extract image url paths
import time

# CONSTANT VARIABLES
BASE_URL = "https://books.toscrape.com/"
ASSETS_BASE = "assets/"
IMAGES_BASE = os.path.join(ASSETS_BASE, "images")
CSV_BASE = os.path.join(ASSETS_BASE, "csv")
# Allowed image file extensions to allow for different or possibly changing formats
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".svg"} # set

def main():
    """
    Inputs url for https://books.toscrape.com/ to generate a list of categories
        - Each category is then processed to determine total pages, total number of books, and book_urls
        - Each category assigns an index to each book on each page and scrapes the book_data
        - Each scraped book outputs a dictionary (book_data)
        - Each book_data dictionary is collected into a list 'all_books_data'
    Outputs:
        - a filtered list of unique book_data dictionaries to write using book_info["universal_product_code"]
        - a total number of images dowsnloaded out of total books found
        - a directory of downloaded images
    """
    csv_file_path = os.path.join(CSV_BASE, "book_data.csv")
    absolute_csv_path = os.path.abspath(csv_file_path)
    print(f"Saving CSV file to {absolute_csv_path}.")

    ### ETL PROCESS 1: Extract, Transform, Load category and book data to csv files
    # EXTRACTION AND TRANSFORMATION PHASES
    try:
        # Step 1: Create a categories dictionary for category pages to scrape
        # noinspection DuplicatedCode
        categories = generate_categories_list(BASE_URL)
        if not categories:
            print("No categories found.")
            return
        else:
            # Print a message displaying all the category names found
            print(f"Categories found: {', '.join(categories.keys())}")

        all_books_data = []  # Initializes a list to accumulate book_info dictionaries

        # Step 2: Iterate over each category to extract total_books, total_pages, and book_urls
        for category_name, category_url in categories.items():
            print(f"\nProcessing category: {category_name}")

            # Calls the function scrape_category with the given category_url and unpacks its return values
            total_books, total_pages, book_urls = scrape_category(category_url)
            print(f"Found {total_books} books over {total_pages} page(s) in {category_name} category.")

            # Step 3: Process each book URL in the category pages
            for index, book_url in enumerate(book_urls, 1):
                print(f"({index}/{total_books}) Scraping book: {book_url}")
                book_info = scrape_book(book_url)
                if book_info:
                    all_books_data.append(book_info)
                else:
                    print(f"Failed to scrape book: {book_url}")

        ### LOADING PHASE
        # Step 4: Write the unique_books_list into the csv folder
        os.makedirs(CSV_BASE, exist_ok=True)  # ensure folder exists
        try:
            write_book_data_csv(all_books_data, csv_file_path)
        except Exception as e:
            # fallback: if book_data.csv write fails, merge category CSVs instead
            print(f"Primary CSV write failed: {e}")
            merge_category_csvs(csv_file_path, CSV_BASE)

        # Step 5: Write category csv files
        print("\nWriting category-specific CSV files...")
        category_names = set(book.get("category") for book in all_books_data if book.get("category"))
        total_written = 0

        for category_name in category_names:
            count = write_category_csv_files(category_name, all_books_data, CSV_BASE)
            total_written += count

        # Step 6: If master CSV is still missing or empty, run fallback again
        if not os.path.exists(csv_file_path) or os.stat(csv_file_path).st_size == 0:
            print("Master CSV missing or empty—running merge fallback again.")
            merge_category_csvs(csv_file_path, CSV_BASE)

        # Final verification
        expected_total = len(all_books_data)
        print(f"\nCategory sorting summary: {total_written} books written into category files.")
        print(f"Total books scraped: {expected_total}")
        if total_written == expected_total:
            print("All books have been successfully sorted into their category CSVs.")
        else:
            print(
                f" Warning: {expected_total - total_written} book(s) were not written. "
                f" Please check for category mismatches or missing data.")

        # Step 7: Download images and store them in /assets/images directory
        download_book_images_from_csv(csv_file_path)


    except Exception as e:
        print(f"An error occurred while processing the data: {e}")

### ETL PROCESS 2 : Function to download images urls once CSV file is written
# noinspection DuplicatedCode
def download_book_images_from_csv(csv_file_path: str):
    """
    Inputs the generated csv file, reads it for image_urls to download the book images for each book
    Outputs each downloaded image file as a .jpg file in /assets/images directory
    """
    # 1. Set the directory where images should be saved: "assets/images/"
    image_dir = os.path.join("assets", "images")

    # 2. If the directory doesn't exist, create it using os.makedirs()
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
        print(f"\nCreated image directory at: {image_dir}\n")
    else:
        print(f"\nImage directory already exists.\n")

    # 3. Open the CSV file using csv.DictReader() obtain the image_urls from each row
    try:
        with open(csv_file_path, newline="", encoding="utf-8") as csvfile:
            reader = list(csv.DictReader(csvfile)) # converts to a list
            image_urls = [
                row["image_url"]
                for row in reader
                if row.get("image_url", "").startswith("http")
                # Ensures that it has both the http prefix and proper image extension suffix
                and os.path.splitext(urlparse(row["image_url"]).path)[1].lower() in ALLOWED_EXTENSIONS
            ]

            print(f"Detected {len(image_urls)} image URLs from CSV.")
            # 4. Count the total number of rows (images to download) and compare to total retreived image_urls
            if not image_urls:
                print("No image URLs found.")
            elif len(image_urls) < len(reader):
                print(f"Warning: {len(reader) - len(image_urls)} entries are missing image URLs.")
                missing_images = [
                    row for row in reader
                    if not row.get("image_url")
                    or not row["image_url"].startswith("http")
                    # Includes check that it conforms with photo extension types to download
                    or os.path.splitext(urlparse(row["image_url"]).path)[1].lower() not in ALLOWED_EXTENSIONS
                ]
                for index, row in enumerate(missing_images, 1):
                    print(f"Missing or unsupported image URL for book entry #{index}: {row.get('title', 'Unknown Title')}")
            else:
                print(f"All book entries have image URLs.\n")

    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return


    total_images = len(image_urls) # set total_images equal to the length of the image_urls list
    failed_downloads = [] # collect list of failed downloaded urls

    # 5. Loop through each row with enumerate():
    for index, image_url in enumerate(image_urls, 1):
        filename = os.path.basename(urlparse(image_url).path) # extract filename from the URL
        local_path = os.path.join(image_dir, filename) # construct full local file path
        # Check if the image already exists at that location
        if os.path.exists(local_path):
            # If so, print a message "already exists" and continue
            print(f"Skipping [{index}/{total_images}]: Image already exists at {local_path} under '{filename}'.")
            continue

        #  Attempt to download image and if failed, store it in failed_downloads list
        try:
            response = requests.get(image_url, stream=True)
            print(f"\nStarting image downloads...\n")
            # If status_code == 200, open the local file in 'wb' mode, write to file, print progress messsage
            if response.status_code == 200:
                with open(local_path, "wb") as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        file.write(chunk)
                print(f"Downloaded ({index}/{total_images}): '{filename}' at '{local_path}'.")
            # If status_code is other than 200, print a failure message
            else:
                print(f"[{index}/{total_images}] Failed to download (status {response.status_code}): {image_url}")
                failed_downloads.append(image_url)
        except Exception as e:
            print(f"[{index}/{total_images}] Error downloading {image_url}: {e}")
            failed_downloads.append(image_url)

    # 6. Manage failed downloads list to reattempt
    if failed_downloads:
        print(f"\nRetrying {len(failed_downloads)} failed downloads...")
        time.sleep(2) # delays execution for 2 seconds before trying again
        for retry_index, image_url in enumerate(failed_downloads, 1):
            # Avoids attempt to download header row 'image_url' or any invalid URL
            if not image_url.startswith("http"):
                print(f"Retry ({retry_index}/{len(failed_downloads)}): Skipped invalid URL: {image_url}")
                continue
            # Sets file name and where it'll be placed in project directory if successfully downloaded
            filename = os.path.basename(urlparse(image_url).path)
            local_path = os.path.join(image_dir, filename)
            try:
                # 'stream' allows to download large sets of images in chunks to save memory
                # timeout if a problem occurs in downloading after 10 seconds
                response = requests.get(image_url, stream=True, timeout=10)
                if response.status_code == 200:
                    with open(local_path, "wb") as file:
                        for chunk in response.iter_content(chunk_size=1024):
                            file.write(chunk)
                    print(f"Retry ({retry_index}/{len(failed_downloads)}): Downloaded {filename}")
                # If the response fails, log the failed attempts and errors
                else:
                    print(
                        f"Retry ({retry_index}/{len(failed_downloads)}): Failed (status {response.status_code}): {image_url}")
            except Exception as e:
                print(f"Retry ({retry_index}/{len(failed_downloads)}): Error downloading {image_url}: {e}")

if __name__ == "__main__":
    main()