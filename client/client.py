import time
import requests
import json
from Utilities.status import Status

BASE_URL = 'http://127.0.0.1:5000'
url = "http://127.0.0.1:5000/upload"


def upload_file(file_path):
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, files=files)
            response.raise_for_status()
            response_json = response.json()
            return response_json['uid']

    except requests.exceptions.HTTPError as error:
        print(error)


def get_status(uid):
    try:
        response = requests.get(f'{BASE_URL}/status/{uid}')
        response.raise_for_status()
        response_json = response.json()
        return Status(response_json['status'], response_json['filename'],
                      response_json['timestamp'], response_json['explanation'])

    except requests.exceptions.HTTPError as error:
        print(error)


def main():
    path = input('Hi! write the path of the file you want to upload: ')
    uid = upload_file(path)
    time.sleep(40)
    status = get_status(uid)
    print(status)


if __name__ == "__main__":
    main()
