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
import psutil

def runSub(MQTT_ELB, UUID, PSK, job_num):
  print('runSub: {}'.format(UUID))
  while True:
    command = ["./mosquitto-1.5.4/client/mosquitto_sub",
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
    "-q",
    "2",
    "--will-topic",
    "$ThingsPro/devices/{}/status".format(UUID),
    "--will-retain",
    "--will-payload",
    "0"]
    proc = subprocess.Popen(command, shell=False)
    print(proc.pid)
    proc.wait()
    
    #command = "./mosquitto-1.5.4/client/mosquitto_sub -h %s -p 8883 -c -i %s -t '$ThingsPro/devices/%s/server' --psk %s --psk-identity %s --will-topic '$ThingsPro/devices/%s/status' --will-retain --will-payload 0 &" % (MQTT_ELB, UUID, UUID, PSK, UUID, UUID)
    #subprocess.Popen(command, shell=True)
    checkAlive(job_num)

def connect(MQTT_ELB, UUID, PSK, job_num):
  thread = threading.Thread(target = runSub, args=(MQTT_ELB, UUID, PSK, job_num,))
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
    command = "./mosquitto-1.5.4/client/mosquitto_pub -h %s -p 8883 -t '%s' --psk '%s' --psk-identity '%s' -q 2 -m '%s' " % (MQTT_ELB, TOPIC, PSK, UUID, json.dumps(data))
    subprocess.Popen(command, shell=True)
    time.sleep(random.randint(20, 100))

def checkAlive(job_num):
  print('checkAlive')
  while True:
    time.sleep(10)
    count = 0
    print('checkAlive loop')
    for proc in psutil.process_iter():
      print(proc.name())
      if proc.name() == "mosquitto_sub":
        count = count + 1

    print(count)
    if(count < int(job_num)):
      break

  """
  while True:
    time.sleep(10)
    try:
      os.kill(pid, 0)
    except OSError:
      break
    
    #random disconnect emulation
    p = random.randint(0, 1000)
    if p == 1:
      os.kill(pid, signal.SIGNAL_SIGTERM)
      break
  """

def onexit():
  command = "ps aux | grep mosquitto_sub | awk '{print $2}' | xargs kill"
  os.system(command)
  print('exit')

atexit.register(onexit)
