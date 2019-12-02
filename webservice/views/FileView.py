import hashlib
import os
import urllib.request
from app import app
from flask import Flask, request, redirect, jsonify
from werkzeug.utils import secure_filename
from models import FileModel, FileSchema

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'exe', '.zip'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
    :param filepath:
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


file_api = Blueprint('safe_files', __name__)
file_schema = FileSchema


@file_api.route('/', methods=['POST'])
def create():
    # check if the post request has the file part
    if 'file' not in request.files:
        resp = jsonify({'message': 'No file part in the request'})
        resp.status_code = 400
        return resp
    file = request.files['file']
    if file.filename == '':
        resp = jsonify({'message': 'No file selected for uploading'})
        resp.status_code = 400
        return resp
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        data = file_schema.load(file)
        files = FileModel(data)
        files.save()

        resp = jsonify({'message': 'File successfully uploaded'})
        resp.status_code = 201
        return resp
    else:
        resp = jsonify({'message': 'Allowed file types are txt, pdf, png, jpg, jpeg, gif'})
        resp.status_code = 400
        return resp


@file_api.route('/', methods=['GET'])
def get_all():
    files = FileModel.get_all_files()
    ser_files = file_schema.dump(files, many=True)
    return custom_response(ser_files, 200)


@file_api.route('/<string:md5>', methods=['GET'])
def get_one(md5):
    file = FileModel.get_one_file_md5(md5)
    if not file:
        return custom_response({'Error': 'File not found'}, 404)
    ser_file = file_schema.dump(file)
    return custom_response(ser_file, 200)


@file_api.route('/<string:sha1>', methods=['GET'])
def get_one(sha1):
    file = FileModel.get_one_file_sha(sha1)
    if not file:
        return custom_response({'Error': 'File not found'}, 404)
    ser_file = file_schema.dump(file)
    return custom_response(ser_file, 200)


@file_api.route('/<string:md5>', methods=['PUT'])
def update(md5):
    req_data = request.get_json()
    data = file_schema.load(req_data, partial=True)
    file = FileModel.get_one_file_md5(md5)
    file.update(data)
    ser_file = file_schema.dump(file)
    return custom_response(ser_file, 200)


@file_api.route('/<string:sha1>', methods=['PUT'])
def update(sha1):
    req_data = request.get_json()
    data = file_schema.load(req_data, partial=True)
    file = FileModel.get_one_file_sha(sha1)
    file.update(data)
    ser_file = file_schema.dump(file)
    return custom_response(ser_file, 200)


@file_api.route('/<string:md5>', methods=['DELETE'])
def delete(md5):
    file = FileModel.get_one_file(md5)
    if not file:
        return custom_response({'Error': 'File not found'}, 404)
    file.delete()
    return custom_response({'Message': 'File deleted'}, 201)


@file_api.route('/<string:md5>' or '/<string:sha1>', methods=['DELETE'])
def delete(sha1):
    file = FileModel.get_one_file(sha1)
    if not file:
        return custom_response({'Error': 'File not found'}, 404)
    file.delete()
    return custom_response({'Message': 'File deleted'}, 201)


def custom_response(res, status_code):
    return Response(
        mimetype="application/json",
        response=json.dumps(res),
        status=status_code
    )
