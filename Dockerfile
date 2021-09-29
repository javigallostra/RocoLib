# start from base
FROM ubuntu:18.04

LABEL maintainer="Juan Gallostra <juangallostra@gmail.com>"

RUN apt-get update -y && \
    apt-get install -y python3.8 python3.8-dev python3-pip

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /rocolib/requirements.txt

WORKDIR /rocolib

RUN pip3 install -r requirements.txt

COPY . /rocolib

CMD [ "python3", "./application.py" ]

