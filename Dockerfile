# start from base
FROM ubuntu:18.04

LABEL maintainer="Juan Gallostra <juangallostra@gmail.com>"

RUN apt-get update -y && \
    apt-get install -y python3.10 python3.10-dev python3-pip

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /rocolib/requirements.txt

WORKDIR /rocolib

ENV DOCKER_ENV=True 

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /rocolib

CMD [ "python3", "./application.py" ]
