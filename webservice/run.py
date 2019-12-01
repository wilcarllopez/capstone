from app import app
import os


if __name__ == '__main__':
    env_name = os.getenv('FLASK_ENV')
    app = app(env_name)
    app.run()