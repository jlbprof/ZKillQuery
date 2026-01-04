FROM python:3.12-slim

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y git
RUN rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/jlbprof/ZKillQuery.git /app/ZKillQuery
RUN ls -la /app
RUN ls -la /app/ZKillQuery

RUN mkdir -p /app/ZKillQueryData

WORKDIR /app/ZKillQuery

RUN git checkout use_a_container

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

