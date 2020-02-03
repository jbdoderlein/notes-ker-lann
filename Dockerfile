FROM python:3-buster

ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code

RUN apt update && \
    apt install -y gettext nginx uwsgi uwsgi-plugin-python3 && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /code/
RUN pip install -r requirements.txt

COPY . /code/

ENTRYPOINT ["/code/entrypoint.sh"]
EXPOSE 8000
