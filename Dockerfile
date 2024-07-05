FROM ubuntu:22.04
RUN apt-get update
ENV DEBIAN_FRONTEND=noninteractive

ADD . /hide
WORKDIR /hide

RUN apt install -y software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa

RUN apt install -y python3-pip
RUN apt install -y postgresql
RUN apt install -y redis
RUN apt install -y sudo
RUN apt install -y wget
RUN apt install -y git
RUN apt install -y vim

RUN pip3 install fastapi==0.111.0
RUN pip3 install uvicorn==0.30.1
RUN pip3 install SQLAlchemy==2.0.31
RUN pip3 install asyncpg==0.29.0
RUN pip3 install aiofiles==24.1.0
RUN pip3 install redis==5.0.7
RUN pip3 install pyotp==2.9.0
RUN pip3 install qrcode==7.4.2
RUN pip3 install cryptography==42.0.8
RUN pip3 install asynctest==0.13.0
RUN pip3 install coverage==7.5.4
RUN pip3 install flake8==7.1.0
RUN pip3 install safety

ADD . /hide
WORKDIR /hide
RUN mkdir /var/log/app
RUN chmod -R 777 /var/log/app

# node exporter
RUN wget https://github.com/prometheus/node_exporter/releases/download/v1.5.0/node_exporter-1.5.0.linux-amd64.tar.gz
RUN tar -xf node_exporter-1.5.0.linux-amd64.tar.gz
RUN mv node_exporter-1.5.0.linux-amd64/node_exporter /usr/local/bin
RUN rm -r node_exporter-1.5.0.linux-amd64*

# postgres exporter
RUN wget https://github.com/wrouesnel/postgres_exporter/releases/download/v0.5.1/postgres_exporter_v0.5.1_linux-amd64.tar.gz
RUN tar -xzvf postgres_exporter_v0.5.1_linux-amd64.tar.gz
RUN mv postgres_exporter_v0.5.1_linux-amd64/postgres_exporter /usr/local/bin
RUN rm -r postgres_exporter_v0.5.1_linux-amd64*

# redis exporter
RUN wget https://github.com/oliver006/redis_exporter/releases/download/v1.18.0/redis_exporter-v1.18.0.linux-amd64.tar.gz
RUN tar xvfz redis_exporter-v1.18.0.linux-amd64.tar.gz
RUN mv redis_exporter-v1.18.0.linux-amd64/redis_exporter /usr/local/bin
RUN rm -r redis_exporter-v1.18.0.linux-amd64*

EXPOSE 80
ENTRYPOINT ["/hide/entrypoint.sh"]
