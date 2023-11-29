import argparse
import os.path
import sys
import time
from urllib.parse import urlsplit, unquote, urljoin

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError("The url has been redirected")


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


def request_repeater(func):
    def wrapper(*args, **kwargs):
        attempt = 0
        max_attempts = 5
        while attempt < max_attempts:
            try:
                return func(*args, **kwargs)
            except requests.HTTPError as err:
                raise err
            except requests.ConnectionError as err:
                if attempt == max_attempts:
                    raise err

                attempt += 1
                if attempt > 1:
                    time.sleep(15)

    return wrapper


@request_repeater
def execute_get_request(url, params=None):
    response = requests.get(url, params=params)
    response.raise_for_status()
    check_for_redirect(response)
    return response


def download_file(url, file_path, params=None):
    response = execute_get_request(url, params=params)
    with open(file_path, "wb") as file:
        file.write(response.content)


if __name__ == "__main__":
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
    parser.add_argument(
        "--start_id",
        help="start book id",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--end_id",
        help="end book id",
        type=int,
        default=10,
    )
    args = parser.parse_args()
    for book_id in range(args.start_id, args.end_id):
        try:
            book_url = f"https://tululu.org/b{book_id}/"
            response = execute_get_request(book_url)
        except requests.HTTPError as err:
            print(f"{err} ({book_url})", file=sys.stderr)
            continue

        book = parse_book_page(book_url, response.text)

        book_name = book.get("name")
        file_path = os.path.join(args.book_folder, f"{book_id}. {book_name}.txt")
        os.makedirs(args.book_folder, exist_ok=True)
        try:
            download_file(f"https://tululu.org/txt.php", file_path, params={"id": book_id})
        except (requests.HTTPError, requests.ConnectionError) as err:
            print(err, file=sys.stderr)

        os.makedirs(args.image_folder, exist_ok=True)
        image_name = os.path.basename(urlsplit(unquote(book.get("image_url"))).path)
        image_path = os.path.join(args.image_folder, image_name)
        if not os.path.exists(image_path):
            try:
                download_file(book.get("image_url"), image_path)
            except (requests.HTTPError, requests.ConnectionError) as err:
                print(err, file=sys.stderr)
