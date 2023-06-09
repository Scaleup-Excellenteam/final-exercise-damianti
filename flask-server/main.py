from flask import Flask, request, jsonify, flash
import os
import uuid
import datetime
from werkzeug.utils import secure_filename
import glob
import json

app = Flask(__name__)
app.secret_key = 'some secret string'
ALLOWED_EXTENSIONS = {'pptx'}
UPLOAD_DIRECTORY = "../uploads"
OUTPUTS_DIRECTORY = "../outputs"
app.config['UPLOAD_DIRECTORY'] = UPLOAD_DIRECTORY


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['POST'])
def upload_file():
    print(request.files)

    if 'file' not in request.files:
        flash('No file part')
        print('file not in files')
        return jsonify(uid="0"), 404

    file = request.files['file']

    if file.filename == '':
        flash('filename empty')
        return jsonify(uid="0"), 404

    if file and allowed_file(file.filename):
        unique_id = str(uuid.uuid4())
        print('allowed file received')
        filename = f'{unique_id}_{datetime.datetime.now()}_{secure_filename(file.filename)}'
        file.save(os.path.join(app.config['UPLOAD_DIRECTORY'], filename))
        return jsonify(uid=unique_id)


@app.route("/status/<uid>", methods=['GET'])
def get_status(uid):

    file_name, uid_number, time_stamp, explanation = None, None, None, None
    response_status = 200

    file_path_upload = glob.glob(os.path.join(UPLOAD_DIRECTORY, f'{uid}*'))
    file_path_output = glob.glob(os.path.join(OUTPUTS_DIRECTORY, f'{uid}*'))

    if file_path_upload:
        split_name = os.path.basename(file_path_upload[0]).split('_')
        uid_number, time_stamp, *file_name_parts = split_name
        file_name = '_'.join(file_name_parts)
        print('Hey hey mf')
        print (f'uid_number is: {uid_number}')
        print (f'timestamp is: {time_stamp}')
        print (f'filename is: {file_name}')
        if file_path_output:
            status = 'done'

            try:
                with open(file_path_output[0], 'r') as f:
                    explanation = json.load(f)
            except Exception as e:
                explanation = str(e)
        else:
            status = 'pending'
    else:
        status = 'not found'
        response_status = 404

    return jsonify(filename=file_name, uid=uid_number, timestamp=time_stamp,
                   status=status, explanation=explanation) \
        , response_status


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':

    if not os.path.exists(UPLOAD_DIRECTORY):
        os.makedirs(UPLOAD_DIRECTORY)

    if not os.path.exists(OUTPUTS_DIRECTORY):
        os.makedirs(OUTPUTS_DIRECTORY)

    app.run()
