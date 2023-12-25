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
    books = soup.select(".ow_px_td table.d_book")
    return [urljoin(url, book.select_one("a")["href"]) for book in books]


def get_total_pages(content):
    soup = BeautifulSoup(content, "lxml")
    return soup.select(".ow_px_td .center .npage")[-1].text


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
    parser.add_argument(
        "--start_page",
        help="start page in the category",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--end_page",
        help="end page in the category",
        type=int,
    )
    parser.add_argument(
        "--dest_folder",
        help="path to the catalog with the parsing results",
        default="books_details",
    )
    parser.add_argument(
        "--skip_imgs",
        help="skips downloading images",
        action="store_true",
    )
    parser.add_argument(
        "--skip_txt",
        help="skips downloading text documents",
        action="store_true",
    )
    args = parser.parse_args()
    downloaded_books = []

    page_id = args.start_page
    end_page = args.end_page or page_id + 1
    progress_bar = tqdm(range(page_id, end_page), position=0, desc="page")
    while int(page_id) < int(end_page):
        try:
            response = execute_get_request(f"https://tululu.org/l55/{page_id}")
        except requests.HTTPError as err:
            print(f"{err} (Page id: {page_id})", file=sys.stderr)
            page_id += 1
            progress_bar.update()
            continue
        except requests.ConnectionError as err:
            print(err, file=sys.stderr)
            time.sleep(30)
            page_id += 1
            progress_bar.update()
            continue

        if not args.end_page:
            end_page = args.end_page = get_total_pages(response.text)
            progress_bar.reset(int(args.end_page) - int(args.start_page))
            progress_bar.update(progress_bar.n)
            progress_bar.refresh()

        page_id += 1
        progress_bar.update()

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

            file_path = None
            if not args.skip_txt:
                book_name = book.get("name")
                file_path = os.path.join(args.book_folder, f"{book_id}. {book_name}.txt")
                os.makedirs(args.book_folder, exist_ok=True)
                try:
                    download_file(f"https://tululu.org/txt.php", file_path, params={"id": book_id})
                except requests.HTTPError as err:
                    print(err, file=sys.stderr)
                    continue
                except requests.ConnectionError as err:
                    print(err, file=sys.stderr)
                    time.sleep(30)

            image_path = None
            if not args.skip_imgs:
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

    os.makedirs(args.dest_folder, exist_ok=True)
    with open(os.path.join(args.dest_folder, "books.json"), "w") as f:
        json.dump(downloaded_books, f, ensure_ascii=False, indent=2)
