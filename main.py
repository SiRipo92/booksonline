from utils.book_scraper import scrape_book, write_csv


def main():
    url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    product_info = scrape_book(url)


    csv_filename = "book_data.csv"
    write_csv(product_info, csv_filename)
    print(f"Data has been written to {csv_filename}")


if __name__ == "__main__":
    main()