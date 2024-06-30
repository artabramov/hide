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
RUN pip3 install asynctest==0.13.0
RUN pip3 install coverage==7.5.4
RUN pip3 install flake8==7.1.0
RUN pip3 freeze > /hide/requirements.txt

ADD . /hide
WORKDIR /hide
RUN mkdir /var/log/app
RUN chmod -R 777 /var/log/app

EXPOSE 80
ENTRYPOINT ["/hide/entrypoint.sh"]
