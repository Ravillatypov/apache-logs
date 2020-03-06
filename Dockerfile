FROM python:3.7-alpine

ENV PYTHONUNBUFFERED 1
EXPOSE 8000

COPY ./requirements.txt /requirements.txt

RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      build-base gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev && \
    pip install -r /requirements.txt && \
    apk del .tmp-build-deps

RUN mkdir /app
WORKDIR /app
COPY . /app

CMD ["gunicorn", "app.wsgi:application", "-b", "0.0.0.0:8000"]
