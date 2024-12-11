FROM python:3.11

RUN apt-get update && \
    apt-get install -y sqlite3 libsqlite3-dev && \
    apt-get clean

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
