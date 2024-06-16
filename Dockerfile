FROM python:3.11
# generate fastapi dockerfile
COPY . /app
WORKDIR /app

RUN pip install poetry
RUN poetry export -f requirements.txt --output requirements.txt
RUN pip install -r requirements.txt

# expose the port 8000
CMD python main.py