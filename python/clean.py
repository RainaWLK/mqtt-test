from aws import dynamodb
from emu import emu, register
import time

items = dynamodb.scan()

print(items)

uuidList = []

for item in items:
  uuid = item["uuid"]
  #psk = item["psk"]
  print("uuid="+uuid)
  #print("psk="+psk)
  uuidList.append(uuid)

  if len(uuidList) > 5:
    res = register.deregister(uuidList)
    uuidList = []
    time.sleep(2)
