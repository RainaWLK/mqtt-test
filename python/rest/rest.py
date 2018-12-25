import os
import requests
import time
import random
import json
import logging

uuidList = []

def remoteGet(uuid):
  url = "{}/api/v1/deviceTasks".format(os.environ.get('URL'))
  headers = {
    'Content-Type': 'application/json',
    'MX-API-TOKEN': os.environ.get('TOKEN')
  }
  body = {
    "deviceUUID": uuid,
    "payload": {
      "method": "get",
      "resource": "/system/properties"
    }
  }

  try:
    logging.debug('--remote GET /devices/{}/settings/serial'.format(uuid))
    r = requests.post(url, headers=headers, data=json.dumps(body))
    if r.status_code == 200:
      resData = json.loads(r.text)
      #logging.debug(resData)
      return 200
  except Exception as e:
      logging.debug("{} get failed".format(uuid))
      logging.debug(e)
      return None

def addList(uuid):
  if uuidList.count(uuid) == 0:
    uuidList.append(uuid)

def resetList():
  uuidList = []

def run():
  while True:
    time.sleep(20)
    counter = 0
    #logging.debug(uuidList)
    for uuid in uuidList:
      statusCode = remoteGet(uuid)
      if statusCode == 200:
        counter += 1
      time.sleep(1)
    #report (use ERROR to force output)
    logging.ERROR("remote test successed: {} / {}".format(counter, len(uuidList)))
