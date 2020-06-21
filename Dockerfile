FROM python:3-alpine

ENV PYTHONUNBUFFERED 1

# Install LaTeX requirements
RUN apk add --no-cache gettext texlive texmf-dist-latexextra texmf-dist-fontsextra nginx gcc libc-dev libffi-dev postgresql-dev libxml2-dev libxslt-dev jpeg-dev

RUN apk add --no-cache bash

RUN mkdir /code
WORKDIR /code
COPY requirements /code/requirements
RUN pip install gunicorn ptpython --no-cache-dir
RUN pip install -r requirements/base.txt -r requirements/cas.txt -r requirements/production.txt --no-cache-dir

COPY . /code/

# Configure nginx
RUN mkdir /run/nginx
RUN ln -sf /dev/stdout /var/log/nginx/access.log && ln -sf /dev/stderr /var/log/nginx/error.log
RUN ln -sf /code/nginx_note.conf_docker /etc/nginx/conf.d/nginx_note.conf
RUN rm /etc/nginx/conf.d/default.conf

ENTRYPOINT ["/code/entrypoint.sh"]
EXPOSE 80

CMD ["./manage.py", "shell_plus", "--ptpython"]
