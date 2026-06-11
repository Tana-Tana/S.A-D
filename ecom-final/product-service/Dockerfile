FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Cert noi bo (Avast SSL scanning) de pip co the tai package qua HTTPS
COPY avast-root-ca.crt /usr/local/share/ca-certificates/avast-root-ca.crt
RUN update-ca-certificates
ENV PIP_CERT=/etc/ssl/certs/ca-certificates.crt

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["sh", "-c", "python manage.py makemigrations products && python manage.py migrate && python manage.py seed_data && python manage.py runserver 0.0.0.0:8001 2>&1"]
