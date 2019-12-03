FROM python:3.7
ADD . /app
WORKDIR /app
RUN pip install pipenv gunicorn
COPY Pipfile* /tmp/
RUN cd /tmp &&  pipenv lock --requirements > requirements.txt
RUN pip install -r /tmp/requirements.txt
RUN chmod u+x ./scripts/initialize.sh
RUN ./scripts/initialize.sh
EXPOSE 8000
CMD ["./scripts/initialize.sh"]