FROM python:3.8-slim-buster

WORKDIR /bot

COPY requirements.txt .

RUN pip install -r requirements.txt

ADD . .