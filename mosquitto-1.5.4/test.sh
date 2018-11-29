#!/bin/sh
MOSQUITTO_PATH=/usr/src/client

SERVER=
UUID=
PSK=

make
$MOSQUITTO_PATH/mosquitto_sub -d -h $SERVER -p 8883 -c -i $UUID -t '$ThingsPro/devices/'$UUID'/server' --psk $PSK --psk-identity $UUID --qos 0 --will-topic '$ThingsPro/devices/'$UUID'/status' --will-retain --will-payload 0
#sleep 600000