#!/usr/bin/env python
  
import sys
import os
import time
import json
import logging
import random
import threading
from emu import emu, register
from rest import rest

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
  rest.addList(cg["uuid"])
  logging.debug('----publish---')
  emu.publish(MQTT_URL, cg["uuid"], cg["psk"])

def runRemoteTest():
  rest.run()

def myjob(cg, job_num):
  if os.environ.get('ENV') != 'dev':
    time.sleep(random.uniform(0, 3600))
  else:
    time.sleep(1)
  #resData = register.getUUID()
  # bug: psk issue
  #cg["uuid"] = "94bea896-659a-42fd-b443-f30dadbd0582"
  #cg["psk"] = "00eab55719659e289957f3274b710c9a2ca76db489d884b3cf155fe55307f60e"
  runEmu(cg, job_num)

if len(sys.argv) != 2:
  print(sys.argv[0], "<Count #> The # means count of CG emu")
  sys.exit(1)

threads = []
cgList = register.getUUID(int(sys.argv[1]))
for i in range(len(cgList)):
  threads.append(threading.Thread(target = myjob, args=(cgList[i], sys.argv[1],)))
  threads[i].start()


restThread = threading.Thread(target = runRemoteTest)
restThread.start()

#myjob(1)