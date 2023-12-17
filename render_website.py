import argparse
import json
import os.path

from jinja2 import Environment, FileSystemLoader, select_autoescape


def render(dest_folder):
    with open(os.path.join(dest_folder, "books.json"), "r") as f:
        books = json.load(f)

    env = Environment(
        loader=FileSystemLoader("."),
        autoescape=select_autoescape(["html", "xml"])
    )
    template = env.get_template("template.html")
    rendered_page = template.render(
        books=books
    )
    with open("index.html", "w", encoding="utf8") as file:
        file.write(rendered_page)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Downloading books from https://tululu.org for local reading.",
    )
    parser.add_argument(
        "--dest_folder",
        help="path to the catalog with the parsing results",
        default="books_details",
    )
    args = parser.parse_args()
    render(args.dest_folder)
