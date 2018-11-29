#!/usr/bin/env python
  
import sys
import os
import time
import json
import random
import threading
from emu import emu, register

MQTT_URL = os.environ.get('MQTT_URL')

def job():
  resData = register.register()
  emu.connect(MQTT_URL, resData["uuid"], resData["psk"])
  time.sleep(10)
  emu.publish(MQTT_URL, resData["uuid"], resData["psk"])


if len(sys.argv) != 2:
  print(sys.argv[0], "<Count #> The # means count of CG emu")
  sys.exit(1)

threads = []
for i in range(int(sys.argv[1])):
  threads.append(threading.Thread(target = job))
  threads[i].start()
  time.sleep(random.uniform(0, 10))

