import os
import markdown
from flask import Flask
from config import app_config
from models import db
from views.FileView import file_api as file_blueprint

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

    @app.route('/', methods=['GET'])
    def index():
        """
        example endpoint
        """
        with open(os.path.dirname(app.root_path) + '/README.md', 'r') as markdown_file:
            content = markdown_file.read()
            return markdown.markdown(content)
    return app