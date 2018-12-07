import boto3
import json

dynamodb = boto3.resource('dynamodb', region_name='us-west-1')
table = dynamodb.Table('Devices')

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
  print(item)
  return item