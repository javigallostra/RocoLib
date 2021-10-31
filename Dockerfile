# start from base
FROM ubuntu:20.04
# to prevent debconf from asking questions
ENV DEBIAN_FRONTEND=noninteractive
ENV DOCKER_ENV=True 

LABEL maintainer="Juan Gallostra <juangallostra@gmail.com>"

RUN apt-get update -y && \
    apt-get install -y python3.10 python3-pip
    # apt-get install -y python3.10 python3.10-dev python3-pip

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements.txt /rocolib/requirements.txt

WORKDIR /rocolib

RUN pip3 install --no-cache-dir -r requirements.txt

COPY . /rocolib

CMD [ "python3", "./application.py" ]
