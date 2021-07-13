FROM python:3.8

WORKDIR /code

RUN pip install vk-api sqlalchemy psycopg2

COPY . /code/
