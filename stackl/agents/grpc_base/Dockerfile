FROM python:3.8.2-slim-buster

WORKDIR /usr/src/app

COPY requirements.txt ./

COPY pip.conf /root/.config/pip/

RUN apt-get update && apt-get install -y --no-install-recommends python-dev gcc build-essential && \
    pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python3", "-u", "./main.py" ]