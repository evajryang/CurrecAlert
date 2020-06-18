import random
import boto3
import json
import datetime

kinesis = boto3.client('kinesis')
def getReferrer():
    
    x = random.randint(10,20)
    x = x*20000+20000000 
    y = x*10000+100000000 
    data = {}
    data['datetime'] = random.randint(x,y)
    data['bid price'] = random.randrange(3,10)
    data['ask price'] = random.randrange(4,20)
    data['volume'] = 0
    now = datetime.datetime.now()
    str_now = now.isoformat()
    data['client_timestamp'] = str_now
    return data


def lambda_handler(event, context):
    
    while True:
        
        data = json.dumps(getReferrer())

        kinesis.put_record(
            StreamName='Forexdata',
            Data=data,
            PartitionKey='partitionkey')
