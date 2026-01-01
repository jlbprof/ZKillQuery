FROM python:3.12-slim

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y git
RUN rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/jlbprof/ZKillQuery.git /app/ZKillQuery

WORKDIR /app/ZKillQuery

RUN git checkout use_a_container

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT [ "/bin/bash", "-c", "cd /app/ZKillQuery && ls -ld * && whereis python3" ]

