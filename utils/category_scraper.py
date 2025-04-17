import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


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
