FROM python:3.9-slim
WORKDIR /app
COPY ./app/requirements.txt /app/requirements.txt

RUN pip3 install -r requirements.txt

EXPOSE 8500

HEALTHCHECK CMD curl --fail http://localhost:8500/_stcore/health

ENTRYPOINT ["streamlit", "run", "main.py", "--server.port=8500", "--server.address=0.0.0.0"]