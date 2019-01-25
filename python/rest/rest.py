import os
import requests
import time
import random
import json
import logging
#from aws import cloudwatch

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
    logging.debug('--remote GET {}/system/properties'.format(uuid))
    r = requests.post(url, headers=headers, data=json.dumps(body))
    if r.status_code == 200:
      resData = json.loads(r.text)
      logging.debug(resData)
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
    try:
      time.sleep(600)
      counter = 0
      time_usage = 0
      #logging.debug(uuidList)
      for uuid in uuidList:
        start = time.time()
        statusCode = remoteGet(uuid)
        time_usage += time.time() - start
        if statusCode == 200:
          counter += 1
        #time.sleep(1)
      #report (use ERROR to force output)
      num = len(uuidList)
      if num > 0:
        logging.error("remote test successed: {} / {} , avg {} ms".format(counter, num, time_usage*1000/num))
        #cloudwatch.put_log_events("remote test successed: {} / {} , avg {} ms".format(counter, len(uuidList), time_usage*1000/len(uuidList)))
    except Exception as e:
      logging.error(e)
