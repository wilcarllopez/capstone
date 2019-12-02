import configparser
import os
from flask import Flask
from config import app_config
from models import db
from views.FileView import file_api as file_blueprint

config = configparser.ConfigParser()
path = os.path.abspath(os.path.dirname(__file__))
config.read(f"{path}{os.sep}config.ini")


def app(env_name):
    """
    Creates the API
    :param env_name: Environment variable
    :return app:
    """
    app = Flask(__name__)
    app.config.from_object(app_config[env_name])
    db.init_app(app)
    app.register_blueprint(file_blueprint, url_prefix='/file/')
    UPLOAD_FOLDER = 'upload'
    directory = f"{os.path.abspath(os.path.dirname(__name__))}{os.sep}{UPLOAD_FOLDER}{os.sep}{filename}"
    app.config['UPLOAD_FOLDER'] = directory

    return app