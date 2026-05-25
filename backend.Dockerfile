# https://www.docker.com/blog/how-to-dockerize-django-app/
# Use the official Python runtime image
FROM python:3.12


# Telemetry
WORKDIR /telemetry

RUN wget https://github.com/open-telemetry/opentelemetry-collector-releases/releases/download/v0.152.0/otelcol_0.152.0_linux_arm64.deb

RUN dpkg -i otelcol_0.152.0_linux_arm64.deb

RUN rm -rf otelcol_0.152.0_linux_arm64.deb

COPY ./.opentelemetry/config/otelcol-metrics-config.yaml .opentelemetry/config/otelcol-metrics-config.yaml

COPY ./.opentelemetry/config/otelcol-default-config.yaml .opentelemetry/config/otelcol-default-config.yaml

RUN nohup bash -c "otelcol --config .opentelemetry/config/otelcol-metrics-config.yaml | otelcol --config .opentelemetry/config/otelcol-default-config.yaml" &


# Set the working directory inside the container
WORKDIR /app
 
# Set environment variables 
# Prevents Python from writing pyc files to disk
ENV PYTHONDONTWRITEBYTECODE=1
#Prevents Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1 
 
# Upgrade pip
RUN pip install --upgrade pip 
 
# Copy the Django project  and install dependencies
COPY requirements.txt  /app/
 
# run this command to install all dependencies 
RUN pip install --no-cache-dir -r requirements.txt
 
# Copy the Django project to the container
COPY . /app/

RUN rm -rf ./.alertmanager \
    && rm -rf ./.dast \
    && rm -rf ./.grafana \
    && rm -rf ./.jenkins-data \
    && rm -rf ./.opentelemetry \
    && rm -rf ./.prometheus \
    && rm -rf ./.vulnerabilities

# Expose the Django port
EXPOSE 8000 8888

# Sanity check
RUN python manage.py check

# Run Django’s development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
