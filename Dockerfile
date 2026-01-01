FROM python:3.12-slim

RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y git
RUN rm -rf /var/lib/apt/lists/*

RUN git clone git@github.com:jlbprof/ZKillQuery.git /app/ZKillQuery && cd /app/ZKillQuery && git checkout use_a_container

RUN pwd
RUN ls -ld *
RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["/bin/bash", "\
    cd /app/ZKillQuery && \
    ./infinite_sleep.sh" ]

