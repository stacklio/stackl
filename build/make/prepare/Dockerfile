FROM python:3.8.1-slim-buster

ARG CORE_VERSION
ARG AGENT_VERSION

ENV CORE_VERSION=${CORE_VERSION}
ENV AGENT_VERSION=${AGENT_VERSION}

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt
COPY main.py .

ENTRYPOINT [ "python", "main.py" ]
