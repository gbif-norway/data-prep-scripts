FROM python:3.8

RUN apt-get update && \
    apt-get install -y vim
RUN adduser user
USER user
ENV PATH=/home/user/.local/bin/:$PATH
EXPOSE 8888
RUN pip install --no-cache-dir pandas xlrd pyproj requests openpyxl jupyterlab
WORKDIR /srv/scripts
