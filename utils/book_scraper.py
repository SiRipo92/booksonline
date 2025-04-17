from bs4 import BeautifulSoup
from bs4.element import AttributeValueList
import requests
import os
import re
import csv
from urllib.parse import urljoin
from typing import Optional

def scrape_book(url: str) -> Optional[dict]:
    """
    Inputs a book page url and extracts, transforms and then loads the data
    Outputs a 'book_info' dictionary to be used to write a csv file with each book's info
    Returns None on failure.
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
        return None

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
    # Initialize as en empty string
    book_description: str = ""
    try:
        description_parent = soup.find('div', id="product_description")
        if description_parent:
            description_paragraph = description_parent.find_next_sibling("p")
            if description_paragraph:
                book_description = description_paragraph.get_text(strip=True)
            else:
                print(f"No description found for {url}.")
                book_description = ""  # Set a default value if no paragraph is found
        else:
            print(f"No description parent element was found for {url}.")
    except Exception as e:
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
            rating_classes = rating_tag.get("class", AttributeValueList())  # e.g., ['star-rating', 'Three']
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
    book_category: Optional[str] = None
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


def write_csv(book_info_list: list[dict], file_path:str) -> None:
    """
    Input: Takes in a book_info dictionary ( from scrape_book() ) and writes it to a CSV file.
    Output: A CSV file with column headers as keys from book_info dictionary and rows for each book's data
    """

    if os.path.exists(file_path):
        remove_csv_duplicate_rows(file_path)

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

    book_info_list = [
        book for book in book_info_list
        if set(book.values()) != set(columns)
    ]

    # Detect duplicates from current file
    existing_upcs = set()
    if os.path.exists(file_path):
        try:
            with open(file_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                existing_upcs = {
                    row["universal_product_code"]
                    for row in reader
                    if "universal_product_code" in row
                }
        except Exception as e:
            print(f"Error reading existing CSV for duplicate checking: {e}")

    # Filter out entries already in the CSV
    unique_new_books = [
        book for book in book_info_list
        if book["universal_product_code"] not in existing_upcs
    ]

    if not unique_new_books:
        print("No unique entries to write.")
        return

    # Append only the new unique entries
    try:
        with open(file_path, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=columns) # type: ignore
            if csvfile.tell() == 0: # Use function tell() to determine if headers have already been written
                writer.writeheader()
            writer.writerows(book_info_list)
        print(f"Data successfully written to CSV file: {file_path}")
    except Exception as e:
        print(f"Error writing to CSV file: {e}")

def remove_csv_duplicate_rows(file_path: str) -> None:
    """
    Removes duplicate rows from an existing CSV file based on 'universal_product_code'.
    Keeps only the first occurrence of each unique UPC.
    """
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = list(csv.DictReader(csvfile))
            if not reader:
                return  # Nothing to prune

            header = reader[0].keys()
            processed_upcs = set()
            unique_rows = []

            for row in reader:
                # Skip row if it's an accidental header
                if set(row.values()) == set(header):
                    continue

                upc = row.get("universal_product_code")
                if upc and upc not in processed_upcs:
                    processed_upcs.add(upc)
                    unique_rows.append(row)

        # Overwrite file with pruned content
        if unique_rows:
            with open(file_path, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=unique_rows[0].keys()) # type: ignore
                writer.writeheader()
                writer.writerows(unique_rows)
            print(f"CSV cleaned of duplicates — {len(reader) - len(unique_rows)} duplicates removed.")
    except Exception as e:
        print(f"Error while removing duplicate entries: {e}")