from scraper.product_scraper import scrape_product, write_csv

def main():
    url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    product_info = scrape_product(url)

    csv_filename = "product_data.csv"
    write_csv(product_info, csv_filename)
    print(f"Data has been written to {csv_filename}")


if __name__ == "__main__":
    main()