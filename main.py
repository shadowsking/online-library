import argparse
import os.path
import sys
import time
from urllib.parse import urlsplit, unquote

import requests

from request_helper import execute_get_request, download_file
from parse_tululu_book import parse_book_page


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
        except requests.ConnectionError as err:
            print(err, file=sys.stderr)
            time.sleep(30)
            continue

        book = parse_book_page(book_url, response.text)

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
