from bs4 import BeautifulSoup # To extract, parse and modify HTML
import requests # To make the HTTP request to the product page
import re # To match and remove expressions to extract the number, ex. in availability "(22 are available)
import csv # To place file in CSV format
from urllib.parse import urljoin  # for the image urls to find their relative paths

# Constants
product_url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000"

## Phase 2: Make these functions we can export to scrape the products
def scrape_product(url):
    """
    Given a product URL, scrape the product data and return it as a dictionary
    """
    page = requests.get(product_url)
    soup = BeautifulSoup(page.content, "html.parser")

    # 1. Get the product_page_url
    product_page_url = product_url

    # 2. Get the product title
    product_title = soup.find("h1").text

    # 3. Get the product's description
    product_description_paragraphs = soup.find_all("p")
    product_description = product_description_paragraphs[-1].text

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

    # 6. Get the product table's characteristics
    table = soup.find("table", class_="table table-striped")
    table_data = {}
    for row in table.find_all("tr"):
        header = row.find("th").text
        data = row.find("td").text
        if header and data:
            table_data[header] = data

    # Recover specific data
    universal_product_code = table_data.get("UPC")
    price_including_tax = table_data.get("Price (incl. tax)")
    price_excluding_tax = table_data.get("Price (excl. tax)")

    # 7. Category (from breadcrumb)
    breadcrumb_list = soup.find("ul", class_="breadcrumb")
    breadcrumb_items = breadcrumb_list.find_all("li")
    category = breadcrumb_items[2].get_text(strip=True) if len(breadcrumb_items) >= 3 else None

    # 8. Image URL (convert relative URL to absolute)
    product_image = soup.find("div", class_="carousel-inner")
    relative_image_url = product_image.find("img").get("src")
    image_url = urljoin(product_url, relative_image_url)

    # Combine all product information into a dictionary
    product_info = {
        "product_page_url": product_page_url,
        "universal_product_code": universal_product_code,
        "title": product_title,
        "price_including_tax": price_including_tax,
        "price_excluding_tax": price_excluding_tax,
        "number_available": number_available,
        "product_description": product_description,
        "category": category,
        "review_rating": review_rating,
        "image_url": image_url,
    }
    return product_info


def write_csv(product_info, csv_filename):
    """
    Given a product_info dictionary and a CSV filename, write the data to CSV.
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
    with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=columns)
        writer.writeheader()
        writer.writerow(product_info)