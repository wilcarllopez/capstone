FROM python:3.7

WORKDIR /app
COPY . /app
RUN pip install gunicorn
COPY Pipfile* /tmp/
RUN pip install -r requirements.txt
RUN chmod u+x ./scripts/initialize.sh
RUN ./scripts/initialize.sh
EXPOSE 8000
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]