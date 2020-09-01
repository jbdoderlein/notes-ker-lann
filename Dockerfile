FROM debian:buster-backports

# Force the stdout and stderr streams to be unbuffered
ENV PYTHONUNBUFFERED 1

# Install Django, external apps, LaTeX and dependencies
# Outside Docker, you may also need git, acl, python3-venv, uwsgi, uwsgi-plugin-python3, nginx
RUN apt-get update && \
    apt-get install -t buster-backports -y python3-django python3-django-crispy-forms \
    python3-django-extensions python3-django-filters python3-django-polymorphic \
    python3-djangorestframework python3-django-cas-server python3-psycopg2 python3-pil \
    python3-babel python3-lockfile python3-pip \
    texlive-latex-extra texlive-fonts-extra texlive-lang-french \
    gettext libjs-bootstrap4 fonts-font-awesome && \
    rm -rf /var/lib/apt/lists/*

# Instal PyPI requirements
COPY requirements.txt /code/
RUN pip3 install -r /code/requirements.txt --no-cache-dir

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
