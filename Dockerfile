FROM debian:buster

# Force the stdout and stderr streams to be unbuffered
ENV PYTHONUNBUFFERED 1

# Install APT requirements
RUN apt-get update && \
    apt-get install -y nginx python3 python3-pip python3-dev \
    uwsgi uwsgi-plugin-python3 python3-venv git acl gettext \
    libjs-bootstrap4 fonts-font-awesome \
    texlive-latex-extra texlive-fonts-extra texlive-lang-french && \
    rm -rf /var/lib/apt/lists/*

# Instal PyPI requirements
COPY requirements /code/requirements
RUN pip install -r requirements/base.txt -r requirements/cas.txt -r requirements/production.txt --no-cache-dir

# Copy code
WORKDIR /code
COPY . /code/

#RUN pip install gunicorn ptpython --no-cache-dir

# Configure nginx
RUN mkdir /run/nginx
RUN ln -sf /dev/stdout /var/log/nginx/access.log && ln -sf /dev/stderr /var/log/nginx/error.log
RUN ln -sf /code/nginx_note.conf_docker /etc/nginx/conf.d/nginx_note.conf
RUN rm /etc/nginx/conf.d/default.conf

ENTRYPOINT ["/code/entrypoint.sh"]
EXPOSE 80

CMD ["./manage.py", "shell_plus", "--ptpython"]
