FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt /app
RUN pip install -r requirements.txt --no-cache-dir

COPY . /app

CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 webapp.wsgi:application