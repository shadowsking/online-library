from urllib.parse import urljoin

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def parse_book_page(url, content):
    soup = BeautifulSoup(content, "lxml")

    title_tag = soup.find(class_="ow_px_td").find("h1")
    book_name = title_tag.text.split("::")[0]
    sanitized_book_name = sanitize_filename(book_name.strip())

    image_url = urljoin(url, soup.find(class_="bookimage").find("img")["src"])
    texts = soup.find_all(class_="texts")
    comments = [text.find(class_="black").text for text in texts]

    parsed_genres = soup.find("span", class_="d_book").find_all("a")
    genres = [d_book.text for d_book in parsed_genres]

    author = soup.find(class_="ow_px_td").find("h1").find("a").text



    return {
        "name": sanitized_book_name,
        "author": author,
        "image_url": image_url,
        "comments": comments,
        "genres": genres
    }
