from urllib.parse import urljoin

from bs4 import BeautifulSoup

from request_helper import execute_get_request


def get_books_urls(url, content):
    soup = BeautifulSoup(content, "lxml")
    books = soup.find(class_="ow_px_td").find_all("table", class_="d_book")
    for book in books:
        yield urljoin(url, book.find("a")["href"])


if __name__ == '__main__':
    response = execute_get_request("https://tululu.org/l55/1")
    for url in get_books_urls(response.url, response.text):
        print(url)
