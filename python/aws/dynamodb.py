import boto3
import json

dynamodb = boto3.resource('dynamodb', region_name='us-west-1')
table = dynamodb.Table('Devices')

def updateUUID(uuid, psk):
  response = table.update_item(
    Key={
      'uuid': uuid
    },
    UpdateExpression="set psk = :p",
    ExpressionAttributeValues={
      ':p': psk
    },
    ReturnValues="UPDATED_NEW"
  )

  print("UpdateItem succeeded:")
  print(json.dumps(response))