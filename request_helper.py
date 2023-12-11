import time

import requests


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError("The url has been redirected")


def request_repeater(func):
    def wrapper(*args, **kwargs):
        attempt = 0
        max_attempts = 5
        while attempt < max_attempts:
            try:
                return func(*args, **kwargs)
            except requests.ConnectionError as err:
                if attempt == max_attempts:
                    raise err

                attempt += 1
                if attempt > 1:
                    time.sleep(15)

    return wrapper


@request_repeater
def execute_get_request(url, params=None):
    response = requests.get(url, params=params)
    response.raise_for_status()
    check_for_redirect(response)
    return response


def download_file(url, file_path, params=None):
    response = execute_get_request(url, params=params)
    with open(file_path, "wb") as file:
        file.write(response.content)
