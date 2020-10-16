FROM python:3.8

RUN apt-get update && \
    apt-get install -y vim

RUN pip install --no-cache-dir pandas xlrd pyproj requests
