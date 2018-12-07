#!/usr/bin/env python
  
import sys
import os
import time
import json
import random
import threading
from emu import emu, register

MQTT_URL = os.environ.get('MQTT_URL')

def runEmu(cg):
  print('----runEmu---')
  emu.connect(MQTT_URL, cg["uuid"], cg["psk"])
  print('----connect done---')
  time.sleep(10)
  print('----publish---')
  emu.publish(MQTT_URL, cg["uuid"], cg["psk"])
  

def job():
  resData = register.getUUID()
  runEmu(resData)


if len(sys.argv) != 2:
  print(sys.argv[0], "<Count #> The # means count of CG emu")
  sys.exit(1)

threads = []
for i in range(int(sys.argv[1])):
  threads.append(threading.Thread(target = job))
  threads[i].start()
  time.sleep(random.uniform(0, 10))

