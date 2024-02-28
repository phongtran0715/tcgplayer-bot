FROM python:3.9-slim

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

ENV VIRTUAL_ENV=/opt/venv_vsm
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN python -m venv $VIRTUAL_ENV

RUN apt-get update \
    && apt-get -y install vim libpq-dev gcc apache2 apache2-dev \
    && apt-get -y install libapache2-mod-wsgi-py3 apache2-utils apt-utils gcc make \
    && pip install --upgrade pip \
    && pip install psycopg2 \
    && pip install mod_wsgi

# create work directory
RUN mkdir -p /app
RUN mkdir -p /etc/ssl/certs

# Install dependencies:
COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/

# Start apache2 service
# https://hackmd.io/@linnil1/H1p25uxFU
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf
RUN echo "WSGIPassAuthorization On" >> /etc/apache2/apache2.conf
COPY default.conf /etc/apache2/sites-enabled/000-default.conf
CMD ["apache2ctl", "-D", "BACKGROUND"]