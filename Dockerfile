FROM ubuntu:20.04 AS base

RUN apt-get update
RUN apt-get -y install git python3 python3-pip nano
WORKDIR /sciit
ADD . /sciit
RUN python2 setup.py install_wr
RUN python3 setup.py install
RUN git config --global user.email "sciit@sciit.com"
RUN git config --global user.name "sciit"
RUN git config --global core.editor nano
RUN ln -s /usr/bin/python3 /usr/bin/python
RUN mkdir -p /home/sciit
RUN cp /sciit/demonstration.sh /home/sciit/demonstration.sh
WORKDIR /home/sciit