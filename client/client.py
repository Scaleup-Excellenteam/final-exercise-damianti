import time
import requests
from dataclasses import dataclass


@dataclass
class Status:
    """
    Represents the status of a file upload and its associated information.

    Attributes:
        status (str): The status of the file upload.
        filename (str): The name of the uploaded file.
        timestamp (str): The timestamp of the upload.
        explanation (dict): The explanation associated with the file upload.
    """

    status: str
    filename: str
    timestamp: str
    explanation: dict

    def is_done(self) -> bool:
        """
        Check if the file upload is done.

        Returns:
            bool: True if the status is 'done', False otherwise.
        """
        return self.status == 'done'


class Client:
    """
    Client class to interact with the API for file uploads and status retrieval.

    Attributes:
        BASE_URL (str): The base URL of the API.
        UPLOAD_URL (str): The URL for uploading files.
    """

    BASE_URL = 'http://127.0.0.1:5000'
    UPLOAD_URL = BASE_URL + '/upload'

    def upload_file(self, file_path: str) -> str:
        """
        Upload a file to the API.

        Args:
            file_path (str): The path of the file to upload.

        Returns:
            str: The unique ID (UID) associated with the uploaded file.

        Raises:
            requests.exceptions.HTTPError: If an HTTP error occurs during the upload.
        """
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(self.UPLOAD_URL, files=files)
                response.raise_for_status()
                response_json = response.json()
                return response_json['uid']

        except requests.exceptions.HTTPError as error:
            print(error)
            return None

    def get_status(self, uid: str) -> Status:
        """
        Get the status of a file upload.

        Args:
            uid (str): The unique ID (UID) of the file upload.

        Returns:
            Status: An instance of the Status class representing the status and information of the file upload.

        Raises:
            requests.exceptions.HTTPError: If an HTTP error occurs while retrieving the status.
        """
        try:
            response = requests.get(f'{self.BASE_URL}/status/{uid}')
            response.raise_for_status()
            response_json = response.json()
            return Status(response_json['status'], response_json['filename'],
                          response_json['timestamp'], response_json['explanation'])

        except requests.exceptions.HTTPError as error:
            print(error)
            return None


def main():
    """
    Main function to demonstrate file upload and status retrieval.

    This function prompts the user to enter the path of a file to upload, uploads the file to the API,
    waits for a specified duration, and then retrieves the status of the upload.

    Note:
        The API base URL is assumed to be 'http://127.0.0.1:5000'.

    Returns:
        None
    """
    client = Client()
    path = input('Hi! Write the path of the file you want to upload: ')
    uid = client.upload_file(path)
    if not uid:
        return
    time.sleep(40)

    status1 = client.get_status(uid)

    if not status1:
        return
    print(status1)


if __name__ == "__main__":
    main()
