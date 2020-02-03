FROM python:3.7.4

WORKDIR /usr/src/app

RUN pip install click jinja2 PyYAML

COPY main.py .

ENTRYPOINT [ "python", "main.py" ]