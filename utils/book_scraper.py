from bs4 import BeautifulSoup
import requests
import re
import csv
from urllib.parse import urljoin

def scrape_book(url):
    """
    Inputs a book page url - if it's able to recover the URL then ... if not ?
    Try to recover data we need, transform it, and store it in variables
    Output a dictionary 'book_info'
    """
    book_page = requests.get(url)
    soup = BeautifulSoup(book_page.content, "html.parser")

    # 1. Get the product_page_url
    book_page_url = url

    # 2. Get the product title
    product_title = soup.find("h1").text

    # 3. Get the product's description
    book_description_paragraphs = soup.find_all("p")
    book_description = book_description_paragraphs[-1].text

    # 4. Extract availability into a number format
    availability_text = soup.find("p", class_="instock availability").get_text(strip=True)
    match = re.search(r'\((\d+)\s+available\)', availability_text)
    if match:
        number_available = int(match.group(1))
    else:
        number_available = None

    # 5. Get the review ratings
    rating_tag = soup.find("p", class_="star-rating")
    rating_classes = rating_tag.get("class")  # e.g., ['star-rating', 'Three']
    rating_map = {
        "One": "1/5",
        "Two": "2/5",
        "Three": "3/5",
        "Four": "4/5",
        "Five": "5/5",
    }
    review_rating = "0/5"
    for cls in rating_classes:
        if cls != "star-rating":
            review_rating = rating_map.get(cls, "0/5")

    # 6a. Get the product table's characteristics
    table = soup.find("table", class_="table table-striped")
    table_data = {}
    for row in table.find_all("tr"):
        header = row.find("th").text
        data = row.find("td").text
        if header and data:
            table_data[header] = data

    ## 6b. Recover specific data (UPC, prices with and without taxes)
    universal_product_code = table_data.get("UPC")
    price_including_tax = table_data.get("Price (incl. tax)")
    price_excluding_tax = table_data.get("Price (excl. tax)")

    # 7. Category (from breadcrumb)
    breadcrumb_list = soup.find("ul", class_="breadcrumb")
    breadcrumb_items = breadcrumb_list.find_all("li")
    category = breadcrumb_items[2].get_text(strip=True) if len(breadcrumb_items) >= 3 else None

    # 8. Image URL (convert relative URL to absolute)
    book_image = soup.find("div", class_="carousel-inner")
    relative_image_url = book_image.find("img").get("src")
    image_url = urljoin(url, relative_image_url)

    # Combine all product information into a dictionary
    book_info = {
        "product_page_url": book_page_url,
        "universal_product_code": universal_product_code,
        "title": product_title,
        "price_including_tax": price_including_tax,
        "price_excluding_tax": price_excluding_tax,
        "number_available": number_available,
        "product_description": book_description,
        "category": category,
        "review_rating": review_rating,
        "image_url": image_url,
    }
    return book_info


def write_csv(book_info, book_csv_file):
    """
    Inputs : Takes in a parameter of a book_info dictionary 'book_info' created from the scrape_book()function

    Outputs a CSV file 'book_data.csv' (product_info. of dictionary using the book_info dictionary keys as columns
    and their values in rows
    """
    columns = [
        "product_page_url",
        "universal_product_code",
        "title",
        "price_including_tax",
        "price_excluding_tax",
        "number_available",
        "product_description",
        "category",
        "review_rating",
        "image_url",
    ]
    book_csv_filename = "assets/csv/book_data.csv"
    with open(book_csv_filename, "w", newline="", encoding="utf-8") as book_csv_file:
        writer = csv.DictWriter(book_csv_file,fieldnames=columns)
        writer.writeheader()
        writer.writerow(book_info)

    print(f"The {book_csv_filename} has been written")