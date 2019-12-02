FROM python:3.7
ADD . /app
WORKDIR /app
RUN pip install pipenv gunicorn
COPY Pipfile* /tmp/
RUN pip install -r requirements.txt

EXPOSE 8000
CMD ["python","run.py"]