FROM python:3

RUN pip install ansible

WORKDIR /usr/src/ansible