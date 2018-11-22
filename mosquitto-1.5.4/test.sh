#!/bin/sh
MOSQUITTO_PATH=/usr/src/client

SERVER=mqtt.dev.thingspro.xyz
#SERVER=54.67.90.20
UUID=ce796ef8-58f3-4bf3-96f6-8a76c8ee1e45
PSK=6fd056d663ed9d77acc11d27c721f4a8a86b55615d0381947a344dad872b9e32

make
$MOSQUITTO_PATH/mosquitto_sub -d -h $SERVER -p 8883 -c -i $UUID -t '$ThingsPro/devices/'$UUID'/server' --psk $PSK --psk-identity $UUID --qos 0 --will-topic '$ThingsPro/devices/'$UUID'/status' --will-retain --will-payload 0
