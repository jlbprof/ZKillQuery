FROM python:3.12-slim

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y git

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

RUN rm -rf /var/lib/apt/lists/*
RUN mkdir -p /app/ZKillQueryData

RUN git --branch use_a_container clone https://github.com/jlbprof/ZKillQuery.git /app/ZKillQuery

WORKDIR /app/ZKillQuery

RUN ls -la /app
RUN ls -la /app/ZKillQuery
RUN ls -la /app/ZKillQuery/zkill_producer.py

