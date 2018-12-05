#!/bin/env python
import os
import random
import string
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from aws import dynamodb
from emu import emu, register


db = create_engine(os.environ.get("DATABASE_URI", os.environ.get('DATABASE_URI')))
DBsession = sessionmaker(bind=db)
session = DBsession()

def flushDB(delete_items):
  uuids = ""
  for item in delete_items:
    uuids += "('{}'),".format(item["uuid"])
  uuids = uuids[:-1]
  #session.begin()
  #sql = text("CREATE TEMP TABLE tmp AS SELECT t.* FROM device t LEFT JOIN (values {}) d(uuid) ON t.uuid IS NULL".format(uuids))
  #print(sql)
  sql = text("DELETE FROM device WHERE mac LIKE \"03%\"")
  session.execute(sql)
  #session.execute("TRUNCATE device CASCADE;")
  #session.execute("INSERT INTO device SELECT * FROM tmp;")
  session.commit()



def main():
  items = dynamodb.scan()

  print(items)
  flushDB(items)
  uuidList = []

  for item in items:
    uuid = item["uuid"]
    print("uuid="+uuid)
    #print("psk="+psk)
    uuidList.append(uuid)



    if len(uuidList) > 25:
      dynamodb.deleteUUID(uuidList)
      #res = register.deregister(uuidList)
      uuidList = []
      #break
      time.sleep(0.5)

main()