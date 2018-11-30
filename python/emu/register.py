import os
import requests
import time
import random
import json
from aws import dynamodb

def genMac():
  ts = time.time()
  magic = random.randint(10000, 100000000)
  ts = (int(ts*1000000) + magic)%1540000000000000
  mac = '%0.12x'%ts
  return mac



def register():
  url = "{}/api/v1/devices".format(os.environ.get('URL'))
  headers = {
    'Content-Type': 'application/json',
    'MX-API-TOKEN': os.environ.get('TOKEN')
  }
  mac = genMac()
  data = {
    "mac": mac,
    "displayName": "zzzz{}".format(mac),
    "description": "my test device",
    "serialNumber": str(int(time.time()))
  }
  print(data)
  r = requests.post(url, headers=headers, data=json.dumps(data))
  if r.status_code == 200:
    resData = json.loads(r.text)
    print(resData)
    dynamodb.updateUUID(resData["uuid"], resData["psk"])
    return resData

def deregister(data):
  url = "{}/api/v1/devices".format(os.environ.get('URL'))
  headers = {
    'Content-Type': 'application/json',
    'MX-API-TOKEN': os.environ.get('TOKEN')
  }
  print(url)
  print(data)
  r = requests.delete(url, headers=headers, data=json.dumps(data))
  print(r)
  if r.status_code == 200:
    resData = r.text
    print(resData)
    dynamodb.deleteUUID(data)
    return resData

