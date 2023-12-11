from urllib.parse import urljoin

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def parse_book_page(url, content):
    soup = BeautifulSoup(content, "lxml")

    title_tag = soup.select_one(".ow_px_td h1")
    book_name = title_tag.text.split("::")[0]
    sanitized_book_name = sanitize_filename(book_name.strip())

    image_url = urljoin(url, soup.select_one(".bookimage img")["src"])
    texts = soup.select(".texts")
    comments = [text.select_one(".black").text for text in texts]

    genres = [d_book.text for d_book in soup.select("span.d_book a")]
    author = soup.select_one(".ow_px_td h1 a").text

    return {
        "name": sanitized_book_name,
        "author": author,
        "image_url": image_url,
        "comments": comments,
        "genres": genres,
    }
