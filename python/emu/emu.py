#!/usr/bin/env python

import sys
import os
import time
import subprocess
import json
import random
import atexit

def connect(MQTT_ELB, UUID, PSK):
  command = "mosquitto_sub -d -h %s -p 8883 -c -i %s -t '$ThingsPro/devices/%s/server' --psk %s --psk-identity %s --will-topic '$ThingsPro/devices/%s/status' --will-retain --will-payload 0 &" % (MQTT_ELB, UUID, UUID, PSK, UUID, UUID)
  proc = subprocess.Popen(command, shell=True)
  print(proc.pid)

def publish(MQTT_ELB, UUID, PSK):
  print('start publish...')
  data = {
      'data': 'wwan0',
      'code': 200,
      'resource': '/system/properties/defaultRoute',
      'method': 'put'
  }

  route = ['eth0', 'wwan0', 'wlan0']

  while True:
    TOPIC = '$ThingsPro/devices/{}/client'.format(UUID)
    data['data'] = route[random.randint(0, len(route) - 1)]

    #print('pid {}: {}'.format(pid, i))
    command = "mosquitto_pub -d -h %s -p 8883 -t '%s' --psk '%s' --psk-identity '%s' -q 2 -m '%s'" % (MQTT_ELB, TOPIC, PSK, UUID, json.dumps(data))
    subprocess.Popen(command, shell=True)
    time.sleep(random.randint(2, 10))


def onexit():
  command = "ps aux | grep mosquitto_sub | awk '{print $2}' | xargs kill"
  os.system(command)
  print('exit')

atexit.register(onexit)
