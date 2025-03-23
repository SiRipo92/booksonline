from bs4 import BeautifulSoup # To extract, parse and modify HTML
import requests # To make the HTTP request to the product page
import re # To match and remove expressions to extract the number, ex. in availability "(22 are available)
import csv # To place file in CSV format

# Constants
url = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000"
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")

# 1. Get the product_page_url
product_page_url = url

# 2. Get the product title
product_title = soup.find("h1").text


# 3. Get the product's description
product_page = soup.find("article", class_="product-page")
product_description_paragraphs = soup.find_all("p") # Makes a list of all the paragraphs
product_description = product_description_paragraphs[-1].text # Targets the last paragraph in the container

# 4. Extract availability into a number format
availability_text = soup.find("p", class_="instock availability").get_text(strip=True)

## 4a. Use a regex library to extract the number between parentheses
match = re.search(r'\((\d+)\s+available\)', availability_text)
""""
captures the number as a group to extract from the text
(/ d+) creates a capture group so anything can be taken from it later
(/ s+) at least one whitespace character between the captured digits and the next word
"""""

if match:
    number_available = int(match.group(1))
else:
    number_available = None

# 5. Get the review ratings
rating_tag = soup.find("p", class_="star-rating")
rating_classes = rating_tag.get("class") # Get the list of classes (e.g., ['star-rating', 'Three'])

## 5a. Define a mapping from the class name to the numeric rating
rating_map = {
    "One": "1/5",
    "Two": "2/5",
    "Three": "3/5",
    "Four": "4/5",
    "Five": "5/5",
}
## 5b. Initialize the review rating to a default value
review_rating = "0/5"
## 5c.  Iterate over the classes and look for the rating class
for cls in rating_classes:
    if cls != "star-rating":
        review_rating = rating_map.get(cls, "0/5")

# 6. Get the product table's characteristics, store table data, use dictionary to extract from later
table = soup.find("table", class_="table table-striped")
table_data={} # Initialize empty dictionary

for row in table.find_all("tr"): # for each row in the table, extract the header and data text
    header = row.find("th").text
    data = row.find("td").text
    if header and data: # if there is a header and data available, stock it in the table_data under its header
        header_text = str(header)
        data_text = str(data)
        table_data[header] = data

## 6a. Recovering specific data like UPC and Prices
universal_product_code = table_data.get("UPC") #  get the UCP value
price_including_tax = table_data.get("Price (incl. tax)") # get Price including tax
price_excluding_tax = table_data.get("Price (excl. tax)") # get Price excluding tax

# 7. Category (nested inside a <ul> tag with a class 'breadcrumb',
breadcrumb_list = soup.find("ul", class_="breadcrumb")
for breadcrumb in breadcrumb_list.find_all("a"):
    category = str(breadcrumb.text) # Outputs 'Poetry'

# 8. Image URL
product_image = soup.find("div", class_="carousel-inner")
image_url = product_image.find("img").get("src")

######  With all the extracted data above, we can now create a dictionary

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

csv_filename = "product_data.csv"

# Open the CSV file for writing
with open(csv_filename, "w", newline="", encoding="utf-8") as csvfile:
    # Define the column headers in order
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
    print(columns)

    writer = csv.DictWriter(csvfile, fieldnames=columns)
    writer.writeheader()
    writer.writerow(product_info)
print(f"Data has been written to {csv_filename}")
