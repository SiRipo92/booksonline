import os

from bs4 import BeautifulSoup
import requests
import re
import csv
from urllib.parse import urljoin

def scrape_book(url):
    """
    Inputs a book page url
    Extracts, transforms and then loads the data
    Outputs a dictionary 'book_info' with the extracted and transformed data
    """

    try:
        book_page = requests.get(url)
        # If error in HTTP response raise HTTPError
        book_page.raise_for_status()

        if not book_page.content:
            print(f"No content retrieved from {url}.")
            return None
        soup = BeautifulSoup(book_page.content, "html.parser")
    except requests.RequestException as e:
        print(f"Error retrieving URL {url}: {e}")

    # 1. Get the book_page_url
    book_page_url = url

    # 2. Get the book's title
    try:
        h1_tag = soup.find('h1')
        book_title = h1_tag.get_text(strip=True) if h1_tag else "Title not found"
    except Exception as e:
        book_title = "Error extracting title"
        print(f"Error extracting title: {e}")

    # 3. Get the book's description
    # Locate the <div id="product_description">
    try:
        description_parent = soup.find('div', id="product_description")

        if description_parent:
            description_paragraph = description_parent.find_next_sibling("p")
            if description_paragraph:
                book_description = description_paragraph.get_text(strip=True)
            else:
                book_description = "Description not found"
        else:
            book_description = "Description not found."
    except Exception as e:
        book_description = "Error extracting description"
        print(f"Error extracting description: {e}")

    # 4. Extract book's availability into an int
    try:
        availability_tag = soup.find("p", class_="instock availability")
        if availability_tag:
            availability_text = availability_tag.get_text(strip=True)
            match = re.search(r'\((\d+)\s+available\)', availability_text)
            number_available = int(match.group(1)) if match else None
        else:
            number_available = None
    except Exception as e:
        number_available = None
        print(f"Error extracting availability: {e}")

    # 5. Get the review ratings
    try:
        rating_tag = soup.find("p", class_="star-rating")
        if rating_tag:
            rating_classes = rating_tag.get("class", [])  # e.g., ['star-rating', 'Three']
            rating_map = {
                "One": "1/5",
                "Two": "2/5",
                "Three": "3/5",
                "Four": "4/5",
                "Five": "5/5",
            }
            # Default rating in case no rating is found
            review_rating = "0/5"
            for cls in rating_classes:
                if cls != "star-rating":
                    review_rating = rating_map.get(cls, "0/5")
        else:
            review_rating = "Not found"
    except Exception as e:
        review_rating = "0/5"
        print(f"Error extracting rating: {e}")

    # 6a. Get the product table's characteristics
    try:
        table = soup.find("table", class_="table table-striped")
        table_data = {}
        if table:
            rows = table.find_all("tr")
            for row in rows:
                header = row.find("th").get_text(strip=True) if row.find("th") else "Not found"
                data = row.find("td").get_text(strip=True) if row.find("td") else "Not found"
                if header:
                    table_data[header] = data
        else:
            print("No table found")
    except Exception as e:
        table_data = {}
        print(f"Error extracting table: {e}")

    ## 6b. Recover specific data (UPC, prices with and without taxes)
    universal_product_code = table_data.get("UPC", "Not found")
    price_including_tax = table_data.get("Price (incl. tax)", "Not found")
    price_excluding_tax = table_data.get("Price (excl. tax)", "Not found")

    # 7. Category (from breadcrumb)
    try:
        breadcrumb_list = soup.find("ul", class_="breadcrumb")
        if breadcrumb_list:
            breadcrumb_items = breadcrumb_list.find_all("li")
            book_category = breadcrumb_items[2].get_text(strip=True) if len(breadcrumb_items) >= 3 else "Not found"
        else:
            book_category = "Not found"
    except Exception as e:
        print(f"Error extracting category: {e}")

    # 8. Image URL (convert relative URL to absolute)
    try:
        # Locate the carousel container
        image_container = soup.find("div", class_="carousel-inner")
        if image_container:
            # Find the div with classes "item active" inside the container
            active_item = image_container.find("div", class_="item active")
            if active_item:
                # Now find the img tag within the active item
                img_tag = active_item.find("img")
                if img_tag:
                    relative_image_url = img_tag.get("src", "")
                    # Use the site’s base URL instead of the current page URL
                    base_url = "https://books.toscrape.com/"
                    image_url = urljoin(base_url, relative_image_url)
                else:
                    image_url = "Image tag not found"
            else:
                image_url = "Active item not found"
        else:
            image_url = "Image container not found"
    except Exception as e:
        image_url = ""
        print(f"Error extracting image URL: {e}")

    # Combine all product information into a dictionary
    book_info = {
        "product_page_url": book_page_url,
        "universal_product_code": universal_product_code,
        "title": book_title,
        "price_including_tax": price_including_tax,
        "price_excluding_tax": price_excluding_tax,
        "number_available": number_available,
        "product_description": book_description,
        "category": book_category,
        "review_rating": review_rating,
        "image_url": image_url,
    }
    return book_info

def write_csv(book_info, file_path):
    """
    Inputs : Takes in a parameter of a book_info dictionary, which is created from the scrape_book()function

    Outputs a CSV file 'book_data.csv' (book_info. of dictionary using the book_info dictionary keys as columns
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

    file_exists = os.path.exists(file_path)

    try:
        with open(file_path, "a", newline="", encoding="utf-8") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=columns)
            if not file_exists or os.stat(file_path).st_size == 0:
                writer.writeheader()
                print("CSV file created and header written")
            else:
                print("CSV file already exists; appending data.")

            # Debug prints:
            print("Debug: book_info about to be written ->", book_info)
            writer.writerow(book_info)

    except PermissionError as e:
        print(f"Permission error while writing to CSV file: {e}")
    except Exception as e:
        print(f"Error writing to CSV file: {e}")
    else:
        print(f"Data successfully written to CSV file: {file_path}")
