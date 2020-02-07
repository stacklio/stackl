FROM docker:stable-dind

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN apk add --no-cache python3 musl-dev gcc python3-dev g++
RUN pip3 install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python3", "-u", "./main.py" ]