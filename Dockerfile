FROM python:3.12-slim

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y git

RUN rm -rf /var/lib/apt/lists/*
RUN mkdir -p /app/ZKillQueryData

COPY . /app/ZKillQuery

WORKDIR /app/ZKillQuery

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN ls -l /app
RUN ls -l /app/ZKillQuery
RUN ls -l /app/ZKillQuery/zkill_producer.py
RUN ls -l /app/ZKillQuery/zkill_consumer.py


