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
        return categories_dict
    except Exception as e:
        print(f"Error generating categories: {e}")
        return {}

def extract_book_urls(page_url):
    """
    Inputs: a category page URL, extracts all book page URLs on that page
    Outputs: a list of absolute book URLs that can then be scraped and added to csv
    """
    try:
        response = requests.get(page_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        book_urls = []
        # Each book is contained in an <article> with class "product_pod"
        for article in soup.find_all("article", class_="product-pod"):
            h3 = article.find("h3"):
            if h3:


def scrape_category(category_url):
    """
    Inputs the category page url
    Outputs scraped/extracted data for:
      - Total number of books in the category: int count
      - Total number of pages (max 20 books per page): number of pages visited
      - all_book_urls: list of absolute book URLs from the category
      - Each individual book page's url per page (to be used in a loop with my other function scrape_book())
    """

    all_book_urls = []
    current_url = category_url
    page_count = 0

    while True:
        page_count += 1
        print(f"Scraping page {page_count} : {current_url}")

        #Extract book URLs on this page
        page_book_urls = extract_book

    try:
        response = requests.get(category_url)
        response.raise_for_status()
    except Exception as e:
        print(f"Error retrieving category page: {e}")
        return None, None, []

    soup = BeautifulSoup(response.content, "html.parser")

    # Extract total number of books from first <strong> element inside form element's text
    form = soup.find("form", class_="form-horizontal")
    if form:
        first_strong = form.find("strong")
        try:
            total_books = int(first_strong.text.strip())
        except (ValueError, AttributeError):
            print("Could not extract a valid total number of books.")
            total_books = None
    else:
        print("Could not find the results form on the page.")
        total_books = None

    if total_books is None:
        try:
            article_pods = soup.find_all("article", class_="product-pod")
            if article_pods:
                for article_pod in article_pods:
                    book_url = article_pod.get("a", "href")
                    total_books += 1
                    print(total_books, book_url)
            else:
                print("Could not find books on page")
        except Exception as e:
            print(f"Error extracting total number of books: {e}")
    else:
        total_books = []


    # Calculate total pages, assuming 20 books per page.
    total_pages = math.ceil(total_books / 20)

    # Retrieve all paginated page URLs.
    book_urls = []
    current_url = category_url
    while True:
        book_urls.append(current_url)
        next_li = soup.find("li", class_="next")
        if next_li:
            next_a = next_li.find("a")
            if next_a:
                next_href = next_a.get("href")
                # Use urljoin to compute the next page's absolute URL.
                current_url = urljoin(current_url, next_href)
                # Fetch new page content for further checking.
                response = requests.get(current_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")
            else:
                break
        else:
            break

    return total_books, total_pages, book_urls

def scrape_category_pages(category_url, book_urls, current_url, total_books, total_pages ):
    """
    Inputs: Given a list of categories, a list of category page urls, and a list of book page urls,
    Outputs: the function loops through all the links to read/write the book_data.csv file for all the books
    """
    categories_dict = generate_categories_list(BASE_URL)
    for category in categories_dict.values():
        try:
            requests = requests.get(category)
            requests.raise_for_status()
            soup = BeautifulSoup(requests.content, "html.parser")
            soup.prettify()
            scrape_category(category)
        except Exception as e:
            print(f"Error scraping category page: {e}")
    else:
        if category_url not in categories_dict:
            if book_urls:
                while book_urls.len() > 20 and < total_books and total_pages > 1:
                    new_request = requests.get(book_urls)
                    requests.raise_for_status()
                    book_soup = BeautifulSoup(new_request.content, "html.parser")
                    book_soup.prettify()
                    scrape_book(book_urls)
                    break
            else:
                return