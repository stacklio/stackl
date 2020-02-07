FROM python:3.8.0-buster

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 50051

CMD [ "python", "-u", "./main.py" ]