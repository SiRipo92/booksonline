import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import csv

BASE_URL = "https://books.toscrape.com/"
category_page = urljoin(BASE_URL, "catalogue/category/books/mystery_3/index.html")

def generate_categories_list(base_url=BASE_URL):
    """
    Inputs:
      - base_url: The base URL for the Books to Scrape site.
    Outputs:
      - A dictionary where keys are category names (e.g., "Mystery", "Travel")
        and values are the corresponding absolute URLs for those category pages.
    """
    try:
        response = requests.get(base_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # The categories are in the sidebar within a <ul> with class "nav nav-list"
        nav_list = soup.find("ul", class_="nav nav-list")
        if not nav_list:
            print("Could not find the navigation list for categories.")
            return {}

        # The actual list of categories is in the nested <ul> inside the main <ul>
        sub_list = nav_list.find("ul")
        if not sub_list:
            print("Could not find the sub-list containing categories.")
            return {}

        categories_dict = {}
        for li in sub_list.find_all("li"):
            a_tag = li.find("a")
            if a_tag:
                # Extract the category name and clean up whitespace
                category_name = a_tag.get_text(strip=True)
                # The href is a relative URL; convert it to an absolute URL
                relative_url = a_tag.get("href")
                category_url = urljoin(base_url, relative_url)
                categories_dict[category_name] = category_url
        # Return a categories_dict object where keys are category names and values are their initial URLs
        return categories_dict
    except Exception as e:
        print(f"Error generating categories: {e}")
        return {}

def scrape_category(category_url):
    """
    Inputs: a category_url obtained from the function 'generate_categories_list'
    Outputs:
        - a list of all book URLs to scrape from the inputted url
        - a total number of pages within each category page using its pagination button
        - total number of books within each paginated category page
    """

    all_book_urls = [] # Initialize an empty list to hold all book urls to scrape
    current_url = category_url # The landing page of the category is our starting point
    page_count = 0 # The page_count is initialized to zero and increased with each 'next' page available

    while True:
        # Increase the page count for every category page url found
        page_count += 1
        print(f"\nProcessing page {page_count}: {current_url}")

        # Call function to extract book urls and append the empty list
        books_on_category_page = extract_book_urls(current_url)
        print(f"Found {len(books_on_category_page)} book URLs on this page.")
        all_book_urls.extend(books_on_category_page)

        # Attempt to :
        # - get the parsed HTML content of category page,
        # - retrieve the paginated url link for next pages
        # If not successful, terminate the script for that category and print error
        try:
            response = requests.get(current_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            next_li = soup.find("li", class_="next")

            if next_li:
                next_a = next_li.find("a")
                if next_a:
                    next_href = next_a.get("href")
                    current_url = urljoin(current_url, next_href)
                    print("Next page found; updating URL...")
                else:
                    break
            else:
                break

        except Exception as e:
            print(f"Error extracting book URLs from {current_url}: {e}")

    # Count the total number of books and pages from category
    total_books = len(all_book_urls)
    total_pages = page_count

    # Return the deconstructed data for total books, total pages and the list of all_book_urls
    # Purpose: scrape all book urls and provide clear, printed messages while scraping categories
    return total_books, total_pages, all_book_urls

def extract_book_urls(category_page_url):
    """
    Inputs a category page url obtained from the function 'scrape_category(category_url)'
    Outputs the scraped book_urls for each article on each page
    """
    try:
        response = requests.get(category_page_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        book_urls = [] # Initialize empty book_urls list

        # Loop through each <article> element with class "product_pod" to extract book_page_url
        for article in soup.find_all("article", class_="product_pod"):
            h3 = article.find("h3")
            if h3:
                a_tag = h3.find("a")
                if a_tag and a_tag.get("href"):
                    relative_url = a_tag.get("href")
                    absolute_url = urljoin(category_page_url, relative_url)
                    # Get the absolute url and append the book_urls
                    book_urls.append(absolute_url)
        return book_urls
    except Exception as e:
        print(f"Error extracting book URLs from {category_page_url}: {e}")
        return []

# Write Category CSV files
def write_category_csv_files(category_name: str, book_list: list[dict], base_dir: str) -> None:
    """
    Writes a category-specific CSV file containing only the books that belong to the given category.

    Inputs:
        category_name (str): The name of the category (e.g., "Science", "Travel").
        book_list (list[dict]): List of dictionaries representing all books scraped.
        base_dir (str): Path to the base CSV directory (e.g., 'assets/csv').

    Outputs:
        - Creates or updates a CSV file at: <base_dir>/categories/<category_name>.csv
        - Skips existing books already present (by UPC) to avoid duplication.
        - Logs progress and any errors encountered.
    """
    # Step 1: Normalize category name for filename (e.g., 'Science Fiction' -> 'science_fiction')
    sanitized_category_name = category_name.lower().replace(" ", "_")

    # Step 2: Define the full path for categories directory
    categories_dir = os.path.join(base_dir, sanitized_category_name)
    abs_categories_dir = os.path.abspath(categories_dir)

    # Step 3: Create categories directory if it doesn't exist
    if not os.path.exists(categories_dir):
        os.makedirs(categories_dir)
        print(f"Created a new directory for {category_name} in {abs_categories_dir}")

    # Step 4: Define the full CSV path for the current category
    category_csv_path = os.path.join(categories_dir, f"{sanitized_category_name}.csv")

    # Step 5: Define column headers (same as book_data.csv)
    headers = [
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

    # Step 6: Filter books by category name
    # Step 7: If no books for this category, log and return
    # Step 8: Check for existing entries (by UPC) if file exists
    # Step 9: Filter only new books not already written
    # Step 10: Open the file in append or write mode

    pass

