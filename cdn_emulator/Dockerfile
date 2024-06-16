FROM python:3.11 as base
RUN pip install couchdb fastapi

COPY . /app
WORKDIR /app

CMD python main.py