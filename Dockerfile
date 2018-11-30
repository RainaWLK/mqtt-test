FROM ubuntu

RUN apt-get update
RUN apt-get install -y build-essential libssl-dev uuid-dev net-tools libjson-c-dev python3 python3-pip 

#COPY ./mosquitto-1.5.4/ /usr/src/
WORKDIR /usr/src/
COPY ./python/requirements.txt /usr/src/
COPY ./python/ /usr/src/python
COPY ./mosquitto-1.5.4/ /usr/src/mosquitto-1.5.4/
RUN pip3 install -r requirements.txt
RUN cd /usr/src/mosquitto-1.5.4/ && make


#RUN make
