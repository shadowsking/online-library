import os.path
from urllib.parse import urlsplit, unquote, urljoin

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError("The url has been redirected")


def get_book(book_id):
    response = requests.get(f"https://tululu.org/b{book_id}/")
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except requests.HTTPError:
        return

    soup = BeautifulSoup(response.text, 'lxml')
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
    return {
        "file_name": f"{book_id}. {book_name}.txt",
        "image_url": image_url
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
    book_folder = "books"
    image_folder = "images"
    for folder in [book_folder, image_folder]:
        os.makedirs(folder, exist_ok=True)

    for index in range(1, 11):
        book = get_book(index)
        if not book:
            continue

        file_name = book.get("file_name")
        os.makedirs(book_folder, exist_ok=True)
        url = f"https://tululu.org/txt.php?id={index}"
        download_txt(url, file_name, folder)

        os.makedirs(image_folder, exist_ok=True)
        download_image(book.get("image_url"), folder=image_folder)
