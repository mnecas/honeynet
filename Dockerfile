# syntax=docker/dockerfile:1
FROM ubuntu:latest

COPY . /code/
WORKDIR /code
COPY requirements.txt /code/
RUN chown -R root:root /code/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update -y
RUN apt install python3 python3-pip curl -y
RUN pip3 install -r requirements.txt
# Install docker and docker compose
RUN curl -o /root/docker.tgz https://get.docker.com/builds/Linux/x86_64/docker-1.12.5.tgz && tar -C /root -xvf /root/docker.tgz && mv /root/docker/docker /usr/local/bin/docker && rm -rf /root/docker*
RUN curl -L https://github.com/docker/compose/releases/download/1.7.1/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose && chmod +x /usr/local/bin/docker-compose

