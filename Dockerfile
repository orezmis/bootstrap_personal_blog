FROM python:3.8-alpine
RUN apk update && apk upgrade
RUN apk add --no-cache pkgconfig \
                       gcc \
                       openldap \
                       libcurl \
                       gpgme-dev \
                       libc-dev \
                       postgresql-dev \
                       python3-dev \
                       musl-dev \
                       zlib-dev \
                       jpeg-dev \
                       && rm -rf /var/cache/apk/*

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app
COPY . /app

ENTRYPOINT if [ ! -d ./venv/ ]; then \
echo "[INFO] >> Installing dependencies, please wait..." && \
python -m venv ./venv && \
source ./venv/bin/activate && \
pip install --upgrade pip && \
pip install -r requirements.txt && \
cd ./server && gunicorn api.wsgi:application --bind 0.0.0.0:8000 \
;else \
echo "[INFO] >> Ready to luanch server, checking new dependencies, please wait..." && \
source ./venv/bin/activate && \
pip install -r requirements.txt && \
cd ./server && gunicorn api.wsgi:application --bind 0.0.0.0:8000 \
;fi
