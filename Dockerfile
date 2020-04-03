FROM python:3-buster

ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code

RUN apt update && \
    apt install -y gettext nginx uwsgi uwsgi-plugin-python3 && \
    rm -rf /var/lib/apt/lists/*

# Install LaTeX requirements
RUN apt update && \
    apt install -y texlive-latex-extra texlive-fonts-extra texlive-lang-french && \
    rm -rf /var/lib/apt/lists/*

COPY . /code/

# Comment what is not needed
RUN pip install -r requirements/base.txt
RUN pip install -r requirements/cas.txt
RUN pip install -r requirements/production.txt

ENTRYPOINT ["/code/entrypoint.sh"]
EXPOSE 8000
