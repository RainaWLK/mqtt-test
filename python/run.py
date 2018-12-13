#!/usr/bin/env python
  
import sys
import os
import time
import json
import random
import threading
from emu import emu, register

MQTT_URL = os.environ.get('MQTT_URL')

def runEmu(cg, job_num):
  print('----runEmu---')
  emu.connect(MQTT_URL, cg["uuid"], cg["psk"], job_num)
  print('----connect done---')
  time.sleep(10)
  print('----publish---')
  emu.publish(MQTT_URL, cg["uuid"], cg["psk"])
  

def myjob(job_num):
  time.sleep(random.uniform(0, 600))
  resData = register.getUUID()
  runEmu(resData, job_num)


if len(sys.argv) != 2:
  print(sys.argv[0], "<Count #> The # means count of CG emu")
  sys.exit(1)

threads = []
for i in range(int(sys.argv[1])):
  threads.append(threading.Thread(target = myjob, args=(sys.argv[1],)))
  threads[i].start()

