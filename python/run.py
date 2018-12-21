#!/usr/bin/env python
  
import sys
import os
import time
import json
import logging
import random
import threading
from emu import emu, register

if os.environ.get('ENV') == 'dev':
  logging.basicConfig(level=logging.DEBUG)
else:
  logging.basicConfig(level=logging.ERROR)

MQTT_URL = os.environ.get('MQTT_URL')

def runEmu(cg, job_num):
  logging.debug('----runEmu---')
  emu.connect(MQTT_URL, cg["uuid"], cg["psk"], job_num)
  logging.debug('----connect done---')
  time.sleep(10)
  logging.debug('----publish---')
  emu.publish(MQTT_URL, cg["uuid"], cg["psk"])
  

def myjob(job_num):
  if os.environ.get('ENV') != 'dev':
    time.sleep(random.uniform(0, 3600))
  resData = register.getUUID()
  runEmu(resData, job_num)


if len(sys.argv) != 2:
  print(sys.argv[0], "<Count #> The # means count of CG emu")
  sys.exit(1)

threads = []
for i in range(int(sys.argv[1])):
  threads.append(threading.Thread(target = myjob, args=(sys.argv[1],)))
  threads[i].start()


#myjob(1)