"""
A Flask API to handle file upload and checking of processing status for PowerPoint presentations.

This API has three endpoints:
- '/upload': Accepts a POST request with a PowerPoint file, stores the file, and returns a unique identifier.
- '/status/<uid>': Accepts a GET request with a unique identifier and returns the processing status and result if
    available.
- '/shutdown': Accepts a POST request to shut down the server.

Functions:
- allowed_file(filename: str) -> bool: Checks if a filename has a valid extension.
- upload_file() -> jsonify: Handles file upload requests and returns a unique identifier.
- get_status(uid: str) -> jsonify: Handles requests for processing status and returns status and result if available.
- shutdown_server() -> str: Handles a request to shut down the server.
- start_api(): Starts the Flask API server.
- stop_api() -> str: Sends a request to shut down the server.

Dependencies:
- flask: The web framework for building the API.
- os: For interacting with the operating system to manage files.
- uuid: For generating unique identifiers.
- datetime: For working with timestamps.
- werkzeug: For secure filename handling.
- glob: For file path pattern matching.
- json: For working with JSON data.
- requests: For sending HTTP requests.
- dataclasses: For creating a simple data class.
- logging.handlers: For managing log files.

Usage:
- Run this script directly to start the Flask API server.
- Use a tool like curl or Postman to send HTTP requests to the API.

"""

from flask import Flask, request, jsonify, flash
import os
import uuid
import datetime
from werkzeug.utils import secure_filename
import glob
import json
import requests
from dataclasses import dataclass
import logging.handlers

app = Flask(__name__)
app.secret_key = 'some secret string'
ALLOWED_EXTENSIONS = {'pptx'}
UPLOAD_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), "../uploads"))
OUTPUTS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), "../outputs"))
LOGS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), "../logs/server_logs"))

app.config['UPLOAD_DIRECTORY'] = UPLOAD_DIRECTORY

if not os.path.exists(LOGS_DIRECTORY):
    os.makedirs(LOGS_DIRECTORY)

log_file_name = "server.log"
log_file_path = os.path.join(LOGS_DIRECTORY, log_file_name)

handler = logging.handlers.TimedRotatingFileHandler(log_file_path, when="D", interval=1, backupCount=5)
handler.setFormatter(logging.Formatter("[%(levelname)s] %(asctime)s - %(message)s"))
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)


def allowed_file(filename: str) -> bool:
    """
    Check if the given filename has a valid extension.

    Args:
        filename (str): The name of the file.

    Returns:
        bool: True if the file has a valid extension, False otherwise.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@dataclass
class Status:
    status: str
    filename: str
    timestamp: str
    explanation: dict

    def is_done(self) -> bool:
        """
        Check if the status is 'done'.

        Returns:
            bool: True if the status is 'done', False otherwise.
        """
        return self.status == 'done'


@app.route('/upload', methods=['POST'])
def upload_file() -> jsonify:
    """
    Handle the file upload request.

    Returns:
        jsonify: JSON response with the unique ID (uid) of the uploaded file.
    """

    if 'file' not in request.files:
        app.logger.info('No file part')
        return jsonify(uid="0"), 404

    file = request.files['file']

    if file.filename == '':
        app.logger.info('Empty filename')
        return jsonify(uid="0"), 404

    if file and allowed_file(file.filename):
        unique_id = str(uuid.uuid4())
        print('allowed file received')
        filename = f'{unique_id}_{datetime.datetime.now()}_{secure_filename(file.filename)}'
        file.save(os.path.join(app.config['UPLOAD_DIRECTORY'], filename))
        app.logger.info('File uploaded: %s', filename)
        return jsonify(uid=unique_id)


@app.route("/status/<uid>", methods=['GET'])
def get_status(uid: str) -> jsonify:
    """
    Get the status of a file by its unique ID (uid).

    Args:
        uid (str): The unique ID of the file.

    Returns:
        jsonify: JSON response with the status, filename, timestamp, and explanation (if available).
    """
    file_name, uid_number, time_stamp, explanation = None, None, None, None
    response_status = 200

    file_path_upload = glob.glob(os.path.join(UPLOAD_DIRECTORY, f'{uid}*'))
    file_path_output = glob.glob(os.path.join(OUTPUTS_DIRECTORY, f'{uid}*'))

    if file_path_upload:
        split_name = os.path.basename(file_path_upload[0]).split('_')
        uid_number, time_stamp, *file_name_parts = split_name
        file_name = '_'.join(file_name_parts)
        if file_path_output:
            status = 'done'

            try:
                with open(file_path_output[0], 'r') as f:
                    explanation = json.load(f)
            except Exception as e:
                explanation = str(e)
                app.logger.error('Error reading output file: %s', explanation)
        else:
            status = 'pending'
    else:
        status = 'not found'
        response_status = 404

    app.logger.info('Status requested: uid=%s, status=%s', uid_number, status)

    return jsonify(filename=file_name, uid=uid_number, timestamp=time_stamp,
                   status=status, explanation=explanation), response_status


@app.route('/shutdown', methods=['POST'])
def shutdown_server() -> str:
    """
    Shutdown the Flask server.

    Returns:
        str: Response message indicating the server is shutting down.
    """
    if 'werkzeug.server.shutdown' not in request.environ:
        raise RuntimeError('Not running with the Werkzeug Server')
    app.logger.warning('Shutting down server')
    request.environ['werkzeug.server.shutdown']()
    return 'Server shutting down...'


def start_api():
    """
    Start the Flask API server.

    Creates the necessary directories for uploads and outputs and runs the Flask app.
    """
    try:
        if not os.path.exists(UPLOAD_DIRECTORY):
            os.makedirs(UPLOAD_DIRECTORY)

        if not os.path.exists(OUTPUTS_DIRECTORY):
            os.makedirs(OUTPUTS_DIRECTORY)

        app.run(debug=True)
    finally:
        stop_api()


def stop_api() -> str:
    """
    Stop the Flask API server.

    Sends a shutdown request to the server.

    Returns:
        str: Response message indicating the server is shutting down.
    """
    app.logger.warning('Request to stop server')
    shutdown = requests.post('http://127.0.0.1:5000/shutdown')
    return shutdown.text


if __name__ == '__main__':
    start_api()
