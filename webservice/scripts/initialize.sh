#!/bin/bash
python ./manage.py db init
python ./manage.py db migrate
python ./manage.py db upgrade
gunicorn -b 0.0.0.0:8000 app:app