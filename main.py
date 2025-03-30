from utils.book_scraper import scrape_book, write_csv


def main():
    url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    product_info = scrape_book(url)


    book_csv_file = "/assets/csv/book_data.csv"
    write_csv(product_info, book_csv_file)
    print(f"Data has been written to {book_csv_file}")


if __name__ == "__main__":
    main()