FROM python:3.8

WORKDIR /code

## Install dependencies
RUN pip install -U pip wheel
COPY requirements.txt .
RUN pip install -r requirements.txt

## Install java
RUN apt update -y
RUN apt install default-jdk -y


COPY . .

