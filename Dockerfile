FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /app


COPY requirements.txt /app


RUN pip3 install -r /app/requirements.txt --no-cache-dir


COPY /yoga/ /app


WORKDIR /app


COPY entrypoint.sh /app/

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "yoga.wsgi:application", "--bind", "0:8000" ]