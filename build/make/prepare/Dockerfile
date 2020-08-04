FROM python:3.8.1-slim-buster

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt

RUN pip3 install --no-cache-dir -r requirements.txt
COPY main.py .

ENTRYPOINT [ "python", "main.py" ]
