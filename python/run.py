#!/usr/bin/env python
  
import sys
import os
import time
import json
import random
import threading
from emu import emu

MQTT_ELB = 'mqtt.dev.thingspro.xyz'
UUID = 'ce796ef8-58f3-4bf3-96f6-8a76c8ee1e45'
PSK = '6fd056d663ed9d77acc11d27c721f4a8a86b55615d0381947a344dad872b9e32'

def job(url, uuid, psk):
  emu.connect(url, uuid, psk)
  time.sleep(10)
  emu.publish(url, uuid, psk)


if len(sys.argv) != 2:
  print(sys.argv[0], "<Count #> The # means count of CG emu")
  sys.exit(1)

threads = []
for i in range(int(sys.argv[1])):
  threads.append(threading.Thread(target = job, args = (MQTT_ELB, UUID, PSK)))
  threads[i].start()
  time.sleep(random.uniform(0, 10))

