FROM debian:buster-backports

# Force the stdout and stderr streams to be unbuffered
ENV PYTHONUNBUFFERED 1

# Install Django, external apps, LaTeX and dependencies
RUN apt-get update && \
    apt-get install --no-install-recommends -t buster-backports -y \
    python3-django python3-django-crispy-forms \
    python3-django-extensions python3-django-filters python3-django-polymorphic \
    python3-djangorestframework python3-django-cas-server python3-psycopg2 python3-pil \
    python3-babel python3-lockfile python3-pip python3-phonenumbers ipython3 \
    python3-bs4 python3-setuptools \
    uwsgi uwsgi-plugin-python3 \
    texlive-latex-base texlive-latex-recommended texlive-lang-french lmodern texlive-fonts-recommended \
    gettext libjs-bootstrap4 fonts-font-awesome && \
    rm -rf /var/lib/apt/lists/*

# Instal PyPI requirements
COPY requirements.txt /var/www/note_kfet/
RUN pip3 install -r /var/www/note_kfet/requirements.txt --no-cache-dir

# Copy code
WORKDIR /var/www/note_kfet
COPY . /var/www/note_kfet/

EXPOSE 8080
ENTRYPOINT ["/var/www/note_kfet/entrypoint.sh"]
