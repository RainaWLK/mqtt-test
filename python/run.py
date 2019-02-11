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
    time.sleep(random.uniform(0, 1800))
  else:
    time.sleep(1)
  #resData = register.getUUID()
  # bug: psk issue
  #cg["uuid"] = "f6d1e0ac-066e-4856-9cd9-c7940728f5ee"
  #cg["psk"] = "2b7e7e8b322c1ae61467de9e406c609f7e1d46b3bdff7406e60e996a3922be68"
  #cg["uuid"] = "866b037d-d090-417e-9b3e-1942a9bb93b4"
  #cg["psk"] = "001d1cf797770f1d896369c56d3965dd6ab09e4498ac452670d980598805d744"
  UUID=cg["uuid"]
  UUID_HEAD = UUID[0:24]
  UUID_TAIL = UUID[24:36]
  uuid_tail_int = int(UUID_TAIL, 16)
  time_diff = int(time.time()*10000 % 100000)
  uuid_tail = str(hex(uuid_tail_int+time_diff))[2:]
  if(len(uuid_tail) < 12):
    while(len(uuid_tail) < 12):
      uuid_tail = '0'+uuid_tail
  uuid_time = UUID_HEAD + uuid_tail
  cg["uuid"] = uuid_time
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