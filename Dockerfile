FROM ubuntu

RUN apt-get update
RUN apt-get install -y build-essential libssl-dev uuid-dev
#COPY ./mosquitto-1.5.4/ /usr/src/
#COPY ./test.sh /usr/src/
WORKDIR /usr/src/

#RUN make
