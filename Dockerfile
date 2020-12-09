FROM ubuntu:20.04 AS base

WORKDIR /
RUN apt-get update
RUN apt-get -y install git python3 python3-pip
RUN git clone https://gitlab.com/sciit/sciit
WORKDIR /sciit
RUN python3 setup.py install
RUN git config --global user.email "sciit@sciit.com"
RUN git config --global user.name "sciit"
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN mkdir -p /home/sciit
RUN cp /sciit/demonstration.sh /home/sciit/demonstration.sh
WORKDIR /home/sciit