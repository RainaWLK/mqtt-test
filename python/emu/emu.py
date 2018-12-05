#!/usr/bin/env python

import sys
import os
import time
import subprocess
import json
import random
import atexit
import threading
import signal

def runSub(MQTT_ELB, UUID, PSK):
  while True:
    command = ["./mosquitto-1.5.4/client/mosquitto_sub",
    "-d",
    "-h",
    "{}".format(MQTT_ELB),
    "-p",
    "8883",
    "-c",
    "-i",
    "{}".format(UUID),
    "-t",
    "$ThingsPro/devices/{}/server".format(UUID), 
    "--psk",
    "{}".format(PSK),
    "--psk-identity",
    "{}".format(UUID),
    "--will-topic",
    "$ThingsPro/devices/{}/status".format(UUID),
    "--will-retain",
    "--will-payload",
    "0"]
    proc = subprocess.Popen(command, shell=False)
    print(proc.pid)
    proc.wait()
    checkAlive(proc.pid)

def connect(MQTT_ELB, UUID, PSK):
  thread = threading.Thread(target = runSub, args=(MQTT_ELB, UUID, PSK))
  thread.start()

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
    command = "mosquitto_pub -d -h %s -p 8883 -t '%s' --psk '%s' --psk-identity '%s' -q 2 -m '%s' " % (MQTT_ELB, TOPIC, PSK, UUID, json.dumps(data))
    subprocess.Popen(command, shell=True)
    time.sleep(random.randint(2, 10))

def checkAlive(pid):
  while True:
    try:
      os.kill(pid, 0)
    except OSError:
      break
    else:
      time.sleep(10)
    
    #random disconnect emulation
    p = random.randint(0, 1)
    if p == 1:
      os.kill(pid, signal.SIGNAL_SIGTERM)
      break


def onexit():
  command = "ps aux | grep mosquitto_sub | awk '{print $2}' | xargs kill"
  os.system(command)
  print('exit')

atexit.register(onexit)
