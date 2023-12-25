import argparse
import json
import math
import os.path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def on_reload(dest_file=None, pages_folder=None):
    with open(dest_file, "r") as f:
        books = json.load(f)

    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(["html", "xml"])
    )
    template = env.get_template("template.html")

    books_count = 20
    display_pages = 5
    pages_count = math.ceil(len(books) / books_count)

    for page, iter_books in enumerate(chunked(books, books_count), start=1):
        previous_page = None
        next_page = None
        if page != 1:
            previous_page = os.path.join(pages_folder, f"index{page - 1}.html")
        if page != pages_count:
            next_page = os.path.join(pages_folder, f"index{page + 1}.html")

        pages = {}
        start_num_page = max(1, page - display_pages)
        end_num_page = min(pages_count, page + display_pages)
        for num_page in range(start_num_page, end_num_page):
            pages[num_page] = os.path.join(pages_folder, f"index{num_page}.html")

        rendered_page = template.render(
            iter_books=chunked(iter_books, 2),
            pages=pages,
            current_page=page,
            previous_page=previous_page,
            next_page=next_page
        )
        page_path = os.path.join(pages_folder, f"index{page}.html")
        with open(page_path, "w", encoding="utf8") as file:
            file.write(rendered_page)


def main():
    parser = argparse.ArgumentParser(
        description="Downloading books from https://tululu.org for local reading.",
    )
    parser.add_argument(
        "--dest_file",
        help="path to the catalog with the parsing results",
        default="books.json",
    )
    parser.add_argument(
        "--pages_folder",
        help="html pages folder",
        default="pages",
    )
    args = parser.parse_args()
    os.makedirs(args.pages_folder, exist_ok=True)

    on_reload(args.dest_file, args.pages_folder)
    server = Server()
    server.watch("template.html", lambda: on_reload(args.dest_file, args.pages_folder))
    server.serve(root=".", default_filename=os.path.join(args.pages_folder, "index1.html"))


if __name__ == '__main__':
    main()
