FROM python:3.8.2-slim-buster

WORKDIR /usr/src/app

COPY requirements.txt ./


RUN apt-get update && apt-get install -y --no-install-recommends docker.io=18.09.1+dfsg1-7.1+deb10u1 python-dev git gcc build-essential && \
    pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python3", "-u", "./main.py" ]