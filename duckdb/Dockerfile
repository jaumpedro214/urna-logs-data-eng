FROM jupyter/minimal-notebook

COPY requirements.txt /app/requirements.txt
WORKDIR /app

RUN pip install -r requirements.txt --upgrade
WORKDIR /src

# EXPOSE JUPYTER PORT
EXPOSE 8888
