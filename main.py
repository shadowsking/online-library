import os.path
from urllib.parse import urlsplit, unquote, urljoin

import argparse
import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError("The url has been redirected")


def parse_book_page(content):
    soup = BeautifulSoup(content, 'lxml')
    book_name = sanitize_filename(
        soup.find(class_="ow_px_td")
            .find("h1")
            .text
            .split("::")[0]
            .strip()
    )
    image_url = urljoin(
        "https://tululu.org",
        soup.find(class_="bookimage").find("img")["src"]
    )
    texts = soup.find_all(class_="texts")
    comments = [text.find(class_="black").text for text in texts]

    parsed_genres = soup.find("span", class_="d_book").find_all("a")
    genres = [d_book.text for d_book in parsed_genres]

    author = soup.find(class_="ow_px_td").find("h1").find("a").text

    return {
        "name": book_name,
        "author": author,
        "image_url": image_url,
        "comments": comments,
        "genres": genres
    }


def download_txt(url, file_name, folder="books"):
    response = requests.get(url)
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except requests.HTTPError:
        return

    file_path = os.path.join(folder, file_name)
    with open(file_path, 'wb') as file:
        file.write(response.content)


def download_image(url, folder="books"):
    response = requests.get(url)
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except requests.HTTPError:
        return

    file_name = os.path.basename(urlsplit(unquote(url)).path)
    file_path = os.path.join(folder, file_name)
    if os.path.exists(file_path):
        return

    with open(file_path, 'wb') as file:
        file.write(response.content)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
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
        response = requests.get(f"https://tululu.org/b{book_id}/")
        response.raise_for_status()
        try:
            check_for_redirect(response)
        except requests.HTTPError:
            continue

        book = parse_book_page(response.text)
        if not book:
            continue

        book_name = book.get("name")
        file_name = f"{book_id}. {book_name}.txt"
        url = f"https://tululu.org/txt.php?id={book_id}"
        os.makedirs(args.book_folder, exist_ok=True)
        download_txt(url, file_name, args.book_folder)

        os.makedirs(args.image_folder, exist_ok=True)
        download_image(book.get("image_url"), folder=args.image_folder)
