# Basic Hotel Booking App

## Diagram

![Local Development](diagram/Diagram.png)


## CI/CD

> GitLab: [.gitlab-ci.yml](.gitlab-ci.yml)


## GitOps

> Argo-CD Application Spec: [argo-cd-application-spec.yaml](argo-cd/argo-cd-application-spec.yaml)


## DevSecOps

> Jenkins Container: [compose.yaml](compose.yaml) / [jenkins.Dockerfile](jenkins.Dockerfile)

> Jenkins Pipeline with Vulnerability Scanner, SBOM and SAST: [Jenkinsfile](Jenkinsfile)

> Docker Local Vulnerability Scanner, SBOM and SAST Container: [compose.yaml](compose.yaml) / [vulnerabilities.Dockerfile](vulnerabilities.Dockerfile)

> DAST Scanner Container: [compose.yaml](compose.yaml)

- Vulnerability Scanner: [Trivy](https://github.com/aquasecurity/trivy)

- SBOM: [Syft](https://github.com/anchore/syft) / [Grype](https://github.com/anchore/grype)

- SAST: [Semgrep](https://github.com/semgrep/semgrep)

- DAST: [Nuclei](https://github.com/projectdiscovery/nuclei)


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

> Note: Running in orchestration will require either commenting out to disable or [cloning the react frontend](https://gitlab.com/LarryGeorges-Muala/hotel-booking-frontend-reactjs) code in the `compose.yaml` file to enable it

3. In a separate terminal, run the following to start the RabbitMq queue reader and consume messages:
```bash
python3 manage.py rabbitmq_read_queue --host localhost --queue booking
```
