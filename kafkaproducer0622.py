#!/usr/bin/env python
# coding: utf-8

import csv
import time
from kafka import KafkaProducer
from os import path
from boto3 import client
import json


class CsvEngine:
    def __init__(self, file):
        self.csv_data = csv.reader(file)

    def process_csv(self, f):
        #headers = next(self.csv_data)
        #print('headers:{}'.format(headers)) 

        count = 0
        for line in self.csv_data:  #read csv line by line
            count += 1
            line = {'DataTime Stamp':line[0],'Bid Quote':line[1],'Ask Quote':line[2],'VoLUME':line[3]}
            f(line)
            print(line)
            #time.sleep(0.1)
        return count


#csv2kafka producer
class KafkaEngine:
    def __init__(self):
        self.producer = KafkaProducer(bootstrap_servers=['127.0.0.1:9092'],value_serializer=lambda m: json.dumps(m).encode('utf-8'),
                        key_serializer=str.encode)

    def send_to_csv_data_topic(self, key, data):
        future = self.producer.send('csv-data', key=key, value=data)
        record_metadata = future.get(timeout=10)

    def close(self):
        self.producer.flush(100)
        self.producer.close(100)




'''
s3_client = client('s3')

def lambda_handler(event, context):
   
    record = event['Records'][0]
    bucket = record['s3']['bucket']['name']
    key = record['s3']['object']['key']
    print('bucket:{} key:{}'.format(bucket, key))
    
    input_file = path.join(bucket, key)
    with s3_client.open(input_file, 'r', newline='', encoding='utf-8-sig') as file:
        process_file(file)

'''

def process_file(file):
    kafka = KafkaEngine()
    on_line = lambda line: kafka.send_to_csv_data_topic('S',line)

    csv = CsvEngine(file)
    count = csv.process_csv(on_line)
    print(count)

    kafka.close()





with open('DAT_ASCII_AUDCAD_T_201101.csv', 'r', newline='', encoding='utf-8-sig') as file:
    process_file(file)


