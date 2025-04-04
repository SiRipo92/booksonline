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
        book_title = h1_tag.get_text(strip=True) if h1_tag else None
    except Exception as e:
        book_title = None
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
                print(f"No description found for {url}.")
        else:
            print(f"No description parent element was found")
    except Exception as e:
        book_description = None
        print(f"Error extracting description: {e}")

    # 4. Extract book's availability into an int
    try:
        availability_tag = soup.find("p", class_="availability")
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
        table = soup.find("table", class_="table")
        table_data = {}
        if table:
            rows = table.find_all("tr")
            for row in rows:
                header = row.find("th").get_text(strip=True) if row.find("th") else None
                data = row.find("td").get_text(strip=True) if row.find("td") else None
                if header:
                    table_data[header] = data
        else:
            print("No table found")
    except Exception as e:
        table_data = {}
        print(f"Error extracting table: {e}")

    ## 6b. Recover specific data (UPC, prices with and without taxes)
    universal_product_code = table_data.get("UPC", None)
    price_including_tax = table_data.get("Price (incl. tax)", None)
    price_excluding_tax = table_data.get("Price (excl. tax)", None)

    # 7. Category (from breadcrumb)
    try:
        breadcrumb_list = soup.find("ul", class_="breadcrumb")
        if breadcrumb_list:
            breadcrumb_items = breadcrumb_list.find_all("li")
            book_category = breadcrumb_items[2].get_text(strip=True) if len(breadcrumb_items) >= 3 else None
        else:
            print(f"Book category was not found in breadcrumb list : {breadcrumb_list}")
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
                    image_url = None
            else:
                image_url = None
        else:
            image_url = None
    except Exception as e:
        image_url = None
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
    Input: Takes in a book_info dictionary (from scrape_book()) and writes it to a CSV file.

    Output: If an entry with the same universal_product_code already exists:
      - If data has changed, update that entry.
      - If data is the same, do nothing.
    Otherwise, a new row is appended.
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
    file_path = "assets/csv/book_data.csv"
    # Unique key used to detect duplicates
    unique_key = "universal_product_code"

    existing_rows = []
    file_exists = os.path.exists(file_path)

    if file_exists:
        with open(file_path, "r", newline="", encoding="utf-8") as csv_file:
            try:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    existing_rows.append(row)
            except:
                print(f"Error reading CSV file: {file_path}")
                existing_rows = []

    # Look for duplicate entry using the unique key
    duplicate_found = False
    updated = False
    for index, row in enumerate(existing_rows):
        if row.get(unique_key) == book_info.get(unique_key):
            duplicate_found = True
            # Check if there's been a change in data
            if row != book_info:
                existing_rows[index] = book_info
                updated = True
            break

    if duplicate_found:
        if updated:
            print("Duplicate entry found; data updated.")
        else:
            print("Duplicate entry found: no changes made.")
            return
    else:
        # Append the new entry if no duplicate is found
        existing_rows.append(book_info)
        print("New entry added.")

        # Write all rows (new, updated, or existing) to the CSV file
        try:
            with open(file_path, "a", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=columns)
                writer.writeheader()
                writer.writerows(existing_rows)
            print(f"Data successfully written to CSV file: {file_path}")
        except Exception as e:
            print(f"Error writing to CSV file: {e}")
