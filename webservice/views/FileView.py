import hashlib
import os
import pathlib
from flask import request, jsonify, Blueprint
from werkzeug.utils import secure_filename
from models.FileModel import FileModel, FileSchema

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'exe', 'zip'}

file_api = Blueprint('safe_files', __name__)
file_schema = FileSchema()


def allowed_file(filename):
    """
    Filter necessary files
    :param filename:
    :return: Sliced filename with allowed extension
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def delete_file(file):
    """
    Deletes file
    :param file: File directory
    :return:
    """
    path = f"{os.path.abspath(os.path.dirname(__name__))}" \
           f"{os.sep}uploads{os.sep}{file}"
    if os.path.exists(path):
        os.remove(path)
    else:
        return jsonify({'Message': "File doesn't exists"})


def sha1_hash(filepath):
    """
    Hashing the file through SHA-1
    :param filepath: File directory
    :return sha1:
    """
    blocksize = 65536
    hasher = hashlib.sha1()
    with open(filepath, 'rb') as file:
        buf = file.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = file.read(blocksize)
    sha1 = hasher.hexdigest()
    return sha1


def md5_hash(filepath):
    """
    Hashing the file through MD5
    :param filepath: File directory
    :return md5:
    """
    blocksize = 65536
    hasher = hashlib.md5()
    with open(filepath, 'rb') as file:
        buf = file.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = file.read(blocksize)
    md5 = hasher.hexdigest()
    return md5


@file_api.route('/', methods=['POST'])
def create():
    # check if the post request has the file part
    if 'file' not in request.files:
        resp = jsonify({'Message': 'No file part in the request'})
        resp.status_code = 400
        return resp
    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'Message': 'No file selected for uploading'})
        resp.status_code = 400
        return resp
    if file and allowed_file(file.filename):
        directory = f"{os.path.abspath(os.path.dirname(__name__))}" \
                    f"{os.sep}uploads"
        filename = secure_filename(file.filename)
        file.save(f"{directory}{os.sep}{filename}")  # downloading the file
        filepath = f"{directory}{os.sep}{filename}"  # directory of the file
        md5 = md5_hash(filepath)  # md5 hashing file
        sha = sha1_hash(filepath)  # sha1 hashing file
        metadata = {"filename": filename,
                    "size": str(os.stat(filepath).st_size),
                    "sha1": sha,
                    "md5": md5,
                    "filetypes": pathlib.Path(filepath).suffix
                    }
        req_data = FileModel.get_one_file_sha(sha)
        if req_data:
            os.remove(filepath)
            jsonify({'Error': 'The file is duplicate'})
        data = file_schema.load(metadata)
        files = FileModel(data)
        files.save()
        resp = jsonify({'Message': 'File successfully uploaded'})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify({'Message': 'Allowed file '
                                   'types are txt, pdf, png, jpg, jpeg, gif'})
        resp.status_code = 400
        return resp


@file_api.route('/', methods=['GET'])
def get_all():
    files = FileModel.get_all_files()
    if not files:
        return jsonify({'Error': 'No files found'}, 404)
    ser_files = file_schema.dump(files, many=True)
    return jsonify(ser_files, 200)


@file_api.route('/<string:md5>', methods=['GET'])
def get_one(md5):
    file = FileModel.get_one_file_md5(md5)
    if not file:
        return jsonify({'Error': 'File not found'}, 404)
    ser_file = file_schema.dump(file)
    return jsonify(ser_file, 200)


@file_api.route('/<string:sha1>', methods=['GET'])
def get_one2(sha1):
    file = FileModel.get_one_file_sha(sha1)
    if not file:
        return jsonify({'Error': 'File not found'}, 404)
    ser_file = file_schema.dump(file)
    return jsonify(ser_file, 200)


@file_api.route('/<string:md5>', methods=['PUT'])
def update(md5):
    req_data = request.get_json()
    data = file_schema.load(req_data, partial=True)
    file = FileModel.get_one_file_md5(md5)
    file.update(data)
    ser_file = file_schema.dump(file)
    return jsonify(ser_file, 200)


@file_api.route('/<string:sha1>', methods=['PUT'])
def update2(sha1):
    req_data = request.get_json()
    data = file_schema.load(req_data, partial=True)
    file = FileModel.get_one_file_sha(sha1)
    file.update(data)
    ser_file = file_schema.dump(file)
    return jsonify(ser_file, 200)


@file_api.route('/<string:md5>', methods=['DELETE'])
def delete(md5):
    file = FileModel.get_one_file_md5(md5)
    if not file:
        return jsonify({'Error': 'File not found'}, 404)
    ser_file = file_schema.dump(file)
    file.delete()
    filename = ser_file['filename']
    delete_file(filename)
    return jsonify({'Message': 'File deleted'}, 201)


@file_api.route('/<string:sha1>', methods=['DELETE'])
def delete2(sha1):
    file = FileModel.get_one_file_sha(sha1)
    if not file:
        return jsonify({'Error': 'File not found'}, 404)
    ser_file = file_schema.dump(file)
    file.delete()
    filename = ser_file['filename']
    delete_file(filename)
    return jsonify({'Message': 'File deleted'}, 201)
