from utils.book_scraper import scrape_book, write_csv
import os

def main():
    url = "https://books.toscrape.com/catalogue/in-a-dark-dark-wood_963/index.html"
    book_info = scrape_book(url)
    if not book_info:
        print(f"Scraping failed. Exiting program")
        return

    # Define CSV file path
    file_path = "assets/csv/book_data.csv"
    abs_path = os.path.abspath(file_path)
    print("Writing to CSV at:", abs_path)
    try:
        write_csv(book_info, file_path=file_path)
        print(f"Data has been written to {file_path}")
    except Exception as e:
        print(f"An error occured while writing CSV: {e}")

if __name__ == "__main__":
    main()