# online-library

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
