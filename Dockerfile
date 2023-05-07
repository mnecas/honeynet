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
RUN apt install python3 python3-pip curl cron libpq-dev -y
RUN pip3 install -r requirements.txt
# Install docker and docker compose
RUN apt install docker docker-compose -y


