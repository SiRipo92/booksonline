import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import math

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
    Inputs a category_url obtained from the function 'generate_categories_list',
    Collects the total number of books and pages to scrape along and retrieves each book's url
    Outputs a list of all book URLs to scrape
    """

    all_book_urls = [] # Initialize an empty list to hold all book urls to scrape
    current_url = category_url # The landing page of the category is our starting point
    page_count = 0 # The page_count should be initialized to zero and increased with each 'next' page available

    try:
        response = requests.get(current_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
    except Exception as e:
        print(f"Error extracting book URLs from {current_url}: {e}")

    # Retrieve the next page element <li> element with class 'next'
    next_page = soup.find("li", class_="next")

    # If this element exists, it means there's a link inside so we need to recover the link

    # This function will then call my extract_book_urls(category_page_url) or current-link
    # To extract book data from each page's articles (a book url)
    # and create a list of all_book_urls on that page

    # THIS function, scrape_category() will then increase the page count, set the total pages to the total_count
    # and return the length/total of all_book_urls retrieved


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
                # Be sure this a_tag exists
                # Get the absolute url and append the book_urls
        return book_urls
    except Exception as e:
        print(f"Error extracting book URLs from {category_page_url}: {e}")


