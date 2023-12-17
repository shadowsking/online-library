import argparse
import json
import os.path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server
from more_itertools import chunked


def on_reload(folder=None, pages_folder=None):
    with open(os.path.join(folder, "books.json"), "r") as f:
        books = json.load(f)

    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(["html", "xml"])
    )
    template = env.get_template("template.html")
    for index, iter_books in enumerate(chunked(books, 20)):
        rendered_page = template.render(
            iter_books=chunked(iter_books, 2)
        )
        page_path = os.path.join(pages_folder, f"index{index + 1}.html")
        with open(page_path, "w", encoding="utf8") as file:
            file.write(rendered_page)


def main():
    parser = argparse.ArgumentParser(
        description="Downloading books from https://tululu.org for local reading.",
    )
    parser.add_argument(
        "--dest_folder",
        help="path to the catalog with the parsing results",
        default="books_details",
    )
    parser.add_argument(
        "--pages_folder",
        help="path to the catalog with the parsing results",
        default="pages",
    )
    args = parser.parse_args()
    os.makedirs(args.pages_folder, exist_ok=True)

    on_reload(args.dest_folder, args.pages_folder)
    server = Server()
    server.watch("template.html", lambda: on_reload(args.dest_folder, args.pages_folder))
    server.serve(root=os.path.join(args.pages_folder, "index1.html"))


if __name__ == '__main__':
    main()
