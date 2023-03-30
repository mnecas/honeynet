# syntax=docker/dockerfile:1
FROM ubuntu:latest
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN apt update -y
RUN DEBIAN_FRONTEND=noninteractive apt install python3 python3-pip ansible python3-ansible-runner -y
RUN ansible-galaxy collection install community.vmware community.docker

RUN pip install -r requirements.txt
COPY . /code/
RUN chown -R root:root /code/
