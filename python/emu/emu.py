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
import logging

def runSub(MQTT_ELB, UUID, PSK, job_num):
  while True:
    logging.debug('runSub: {}'.format(UUID))
    command = ["./mosquitto-1.5.4/client/mosquitto_sub",
    "-h",
    "{}".format(MQTT_ELB),
    "-p",
    "8883",
    "-i",
    "{}".format(UUID),
    "-t",
    "$ThingsPro/devices/{}/server".format(UUID), 
    #"--psk",
    #"{}".format(PSK),
    #"--psk-identity",
    #"{}".format(UUID),
    #"--cafile",
    #"./python/rootca.pem",
    "-q",
    "2",
    "--will-topic",
    "$ThingsPro/devices/{}/status".format(UUID),
    "--will-retain",
    "--will-payload",
    "0"]
    if os.environ.get('TLS') == 'true':
      #logging.debug('TLS')
      command.extend(["--cafile", "./python/rootca.pem"])
    else:
      #logging.debug('PSK')
      command.extend(["--psk", "{}".format(PSK), "--psk-identity", "{}".format(UUID)])

    #if os.environ.get('ENV') == 'dev':
    #  command.append("-d")

    proc = subprocess.Popen(command, shell=False)
    #logging.debug(proc.pid)
    proc.wait()
    
    #command = "./mosquitto-1.5.4/client/mosquitto_sub -h %s -p 8883 -c -i %s -t '$ThingsPro/devices/%s/server' --psk %s --psk-identity %s --will-topic '$ThingsPro/devices/%s/status' --will-retain --will-payload 0 &" % (MQTT_ELB, UUID, UUID, PSK, UUID, UUID)
    #subprocess.Popen(command, shell=True)
    checkAlive(job_num)

def connect(MQTT_ELB, UUID, PSK, job_num):
  thread = threading.Thread(target = runSub, args=(MQTT_ELB, UUID, PSK, job_num,))
  thread.start()

def publish(MQTT_ELB, UUID, PSK):
  #logging.debug('start publish...')
  data = {
      'data': 'wwan0',
      'code': 200,
      'resource': '/system/properties/defaultRoute',
      'method': 'put'
  }

  route = ['eth0', 'wwan0', 'wlan0']

  tls = ""
  if os.environ.get('TLS') == 'true':
    #logging.debug('TLS')
    tls = '--cafile ./python/rootca.pem'
  else:
    #logging.debug('PSK')
    tls = "--psk '{}' --psk-identity '{}'".format(PSK, UUID)

  while True:
    TOPIC = '$ThingsPro/devices/{}/client'.format(UUID)
    data['data'] = route[random.randint(0, len(route) - 1)]

    #print('pid {}: {}'.format(pid, i))
    command = "./mosquitto-1.5.4/client/mosquitto_pub -h %s -p 8883 -t '%s' %s -q 2 -m '%s' " % (MQTT_ELB, TOPIC, tls, json.dumps(data))
    subprocess.Popen(command, shell=True)
    time.sleep(random.randint(120, 1800))

def checkAlive(job_num):
  while True:
    time.sleep(10)
    count = 0
    for proc in psutil.process_iter():
      #logging.debug(proc.name())
      try:
        if proc.name() == "mosquitto_sub":
          count = count + 1
      except:
        #do nothing
        continue

    logging.debug("proc count={}".format(count))
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
  logging.info('exit')

atexit.register(onexit)
