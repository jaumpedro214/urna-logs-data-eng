FROM python:3.8-slim

COPY requirements.txt /app/requirements.txt
WORKDIR /app

RUN pip install -r requirements.txt --upgrade
WORKDIR /src

# KEEP CONTAINER RUNNING
CMD ["tail", "-f", "/dev/null"]
