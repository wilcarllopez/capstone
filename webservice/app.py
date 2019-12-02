import configparser
import os
import markdown
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
    app.register_blueprint(file_blueprint, url_prefix='/safe_files/')
    UPLOAD_FOLDER = 'upload'
    directory = f"{os.path.abspath(os.path.dirname(__name__))}{os.sep}{UPLOAD_FOLDER}"
    app.config['UPLOAD_FOLDER'] = directory

    @app.route('/', methods=['GET'])
    def index():
        """
        example endpoint
        """
        with open(os.path.dirname(app.root_path) + '/README.md', 'r') as markdown_file:
            content = markdown_file.read()
            return markdown.markdown(content)
    return app