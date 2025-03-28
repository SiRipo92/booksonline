import requests
from bs4 import BeautifulSoup

url = "https://books.toscrape.com/catalogue/category/books/mystery_3/index.html"
page_category = requests.get(url)
soup = BeautifulSoup(page_category.content,"html.parser")

print(soup.prettify()) 