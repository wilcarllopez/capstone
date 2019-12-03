FROM python:3.7

WORKDIR /app
COPY . /app
RUN pip install pipenv
COPY Pipfile* /tmp/
RUN cd /tmp &&  pipenv lock --requirements > requirements.txt
RUN pip install -r /tmp/requirements.txt
CMD ["/bin/bash"]