# Basic Hotel Booking App

## Diagram

![Local Development](diagram/Diagram.png)

## Backend Setup

> Note: Python 3.12 recommended

- create `.env` file
```bash
SECRET_KEY='some-string'
SENTRY_DNS_DJANGO='https://...ingest.us.sentry.io/...'
```

> Note: see https://sentry.io/pricing/ for a Sentry free-trial account to gain access to the monitor dashboard

- setup application
```bash
python3.12 -m venv ./.venv
source ./.venv/bin/activate
python3 -m pip install -r requirements.txt
python3 manage.py makemigrations
python3 manage.py migrate
```

- Populate database
```bash
python3 manage.py create_units
```

## Backend Execution

1. In terminal (Without Redis, RabbitMq and Prometheus stack):
```bash
python3 manage.py runserver
```

2. Orchestration with Docker Compose (With Redis, RabbitMq and Prometheus stack):
```bash
docker compose up --build --no-deps --force-recreate --remove-orphans
```

> Note: Running in orchestration will require commenting out to disable or [cloning the react frontend](https://gitlab.com/LarryGeorges-Muala/hotel-booking-frontend-reactjs) code in the `compose.yaml` file to enable it

3. In a separate terminal, run the following to start the RabbitMq queue reader and consume messages:
```bash
python3 manage.py rabbitmq_read_queue --host localhost --queue booking
```
