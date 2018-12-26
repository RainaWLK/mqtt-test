import boto3
import json
import logging

dynamodb = boto3.resource('dynamodb', region_name='us-west-1')

TABLE_NAME = 'Devices'
table = dynamodb.Table(TABLE_NAME)


def updateUUID(seq, uuid, psk):
  response = table.update_item(
    Key={
      'id': seq
    },
    UpdateExpression="set #u = :u, psk = :p",
    ExpressionAttributeNames={
      '#u': 'uuid'
    },
    ExpressionAttributeValues={
      ':u': uuid,
      ':p': psk
    },
    ReturnValues="UPDATED_NEW"
  )

  print("UpdateItem succeeded:")
  print(json.dumps(response))

def scan():
  response = table.scan()
  items = response['Items']
  return items

def deleteUUID(uuidList):
  with table.batch_writer() as batch:
    for uuid in uuidList:
        batch.delete_item(
          Key={
            'uuid': uuid
          }
        )

def getUUID(id):
  response = table.get_item(
    Key={
      'id': id
    }
  )
  item = response['Item']
  return item

def sendBatchRead(para):
  try:
    response = dynamodb.batch_get_item(
      RequestItems=para,
      ReturnConsumedCapacity='NONE'
    )
    return response['Responses']
  except Exception as e:
    logging.error(e)

def getUUIDs(idList):
  counter = 0
  queryString = {
    'Devices': {
      'Keys': [],
      'ConsistentRead': False
    }
  }
  output = []
  for id in idList:
    key = {
      'id': id
    }
    queryString[TABLE_NAME]['Keys'].append(key)
    counter += 1

    if counter >= 100:
      res = sendBatchRead(queryString)
      output += res[TABLE_NAME]
      counter = 0
      queryString[TABLE_NAME]['Keys'] = []

  if counter > 0:
    res = sendBatchRead(queryString)
    output += res[TABLE_NAME]

  return output
