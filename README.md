# online-library

https://shadowsking.github.io/online-library/pages/index1.html

Downloading books from https://tululu.org for local reading.

## Installing

1) Clone project
```bash
git clone https://github.com/shadowsking/online-library.git
cd online-library
```

2) Create virtual environments
```bash
python -m venv venv
source venv/scripts/activate
```

3) Install requirements
```bash
pip install -r requirements.txt
```

## Running
```bash
python main.py --start_id 1 --end_id 10
```
Arguments:
- --start_id: start book id
- --end_id: end book id
- --book_folder: folder for downloaded books
- --image_folder: folder for downloaded images

### Downloads books from category
```bash
python parse_tululu_category.py
python parse_tululu_category.py --start_page 1 --end_page 5
```
Arguments:
- --start_page: start page in the category
- --end_page: end page in the category
- --book_folder: folder for downloaded books
- --image_folder: folder for downloaded images
- --dest_folder: path to the catalog with the parsing results
- --skip_imgs: skips downloading images
- --skip_txt: skips downloading text documents

### Render pages
```bash
python render_wibsite.py
```
Arguments:
- --dest_folder: path to the catalog with the parsing results
- --pages_folder: html pages folder
