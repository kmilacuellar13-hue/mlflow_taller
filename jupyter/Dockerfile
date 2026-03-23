FROM jupyter/scipy-notebook:latest

USER root
RUN apt-get update && apt-get install -y libpq-dev && rm -rf /var/lib/apt/lists/*

USER jovyan

RUN pip install --no-cache-dir mlflow boto3 psycopg2-binary sqlalchemy fastparquet
