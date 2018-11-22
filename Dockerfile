FROM ubuntu

RUN apt-get update
RUN apt-get install -y build-essential libssl-dev uuid-dev net-tools libjson-c-dev
#COPY ./mosquitto-1.5.4/ /usr/src/
#COPY ./test.sh /usr/src/
WORKDIR /usr/src/

#RUN make
