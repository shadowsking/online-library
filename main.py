import os.path
import requests


def download_book(url, filename):
    response = requests.get(url)
    response.raise_for_status()
    with open(filename, 'wb') as file:
        file.write(response.content)


if __name__ == '__main__':
    for index in range(10):
        url = f"https://tululu.org/txt.php?id={index + 1}"
        filename = os.path.join("books", f"id{index + 1}.txt")
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        download_book(url, filename)
