import argparse
import json
import os
import re
import sys
import time
from urllib.parse import urlsplit, unquote, urljoin

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from parse_tululu_book import parse_book_page
from request_helper import execute_get_request, download_file


def get_books_urls(url, content):
    soup = BeautifulSoup(content, "lxml")
    books = soup.find(class_="ow_px_td").find_all("table", class_="d_book")
    return [urljoin(url, book.find("a")["href"]) for book in books]


def get_book_id(book_url):
    matched = re.match(r"\S+/b(?P<book_id>\d+)[/]?$", book_url)
    if not matched:
        return

    return matched.groupdict()["book_id"]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Downloading books from https://tululu.org for local reading.",
    )
    parser.add_argument(
        "--book_folder",
        help="book folder location",
        default="books",
    )
    parser.add_argument(
        "--image_folder",
        help="image folder location",
        default="images",
    )
    args = parser.parse_args()
    downloaded_books = []

    for page_id in tqdm(range(1, 4), position=0, desc="page"):
        response = execute_get_request(f"https://tululu.org/l55/{page_id}")
        for book_url in tqdm(
                get_books_urls(response.url, response.text),
                position=1,
                desc="book"
        ):
            try:
                response = execute_get_request(book_url)
            except requests.HTTPError as err:
                print(f"{err} ({book_url})", file=sys.stderr)
                continue
            except requests.ConnectionError as err:
                print(err, file=sys.stderr)
                time.sleep(30)
                continue

            book = parse_book_page(book_url, response.text)
            book_id = get_book_id(book_url)

            book_name = book.get("name")
            file_path = os.path.join(args.book_folder, f"{book_id}. {book_name}.txt")
            os.makedirs(args.book_folder, exist_ok=True)
            try:
                download_file(f"https://tululu.org/txt.php", file_path, params={"id": book_id})
            except requests.HTTPError as err:
                print(err, file=sys.stderr)
            except requests.ConnectionError as err:
                print(err, file=sys.stderr)
                time.sleep(30)

            os.makedirs(args.image_folder, exist_ok=True)
            image_name = os.path.basename(urlsplit(unquote(book.get("image_url"))).path)
            image_path = os.path.join(args.image_folder, image_name)
            if not os.path.exists(image_path):
                try:
                    download_file(book.get("image_url"), image_path)
                except requests.HTTPError as err:
                    print(err, file=sys.stderr)
                except requests.ConnectionError as err:
                    print(err, file=sys.stderr)
                    time.sleep(30)

            downloaded_books.append(
                dict(
                    book_path=file_path,
                    image_src=image_path,
                    **book
                )
            )

    with open("downloaded_books.json", "w") as f:
        json.dump(downloaded_books, f, ensure_ascii=False, indent=2)
