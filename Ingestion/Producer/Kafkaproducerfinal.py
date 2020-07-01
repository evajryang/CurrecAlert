#!/usr/bin/env python
# coding: utf-8

import csv
import time
from kafka import KafkaProducer
from os import path

import boto3
import json
import lazyreader


#class CsvEngine:
#    def __init__(self, file):
#        self.csv_data = csv.reader(file)
#
#    def process_csv(self, f,Type):
#
#
#        count = 0
#        for line in self.csv_data:  #read csv line by line
#            count += 1
#            line = {'DataTime Stamp':line[0],'Bid Quote':line[1],'Ask Quote':line[2],'VoLUME':line[3],'TYPE':Type}
#            f(line)
#            print(line)
#            #time.sleep(0.1)
#        return count


aws_access_key_id = '**********'    #aws connection id
aws_secret_access_key = '*********************'   #aws connection key pair
bucket_name = 'forexdata*********'  #bucket name

class CsvEngine:
    def __init__(self):
        self.s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        
    def process_csv(self, f,Type,key):
        obj = self.s3.get_object(Bucket=bucket_name, Key=key)
        count = 0
        for line in lazyreader.lazyread(obj["Body"], delimiter=b'\n'):
            line = line.decode().replace('\n','').split(',')
            count += 1
            line = {'DataTime Stamp':line[0],'Bid Quote':line[1],'Ask Quote':line[2],'VoLUME':line[3],'TYPE':Type}
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




def process_file(Type,key):
    kafka = KafkaEngine()
    on_line = lambda line: kafka.send_to_csv_data_topic('S',line)

    csvengine = CsvEngine()
    count = csvengine.process_csv(on_line,Type,key)
    print(count)

    kafka.close()



'''
EUR/USD
GBP/USD
USD/JPY
USD/CHF
USD/CAD
AUD/USD
NZD/USD
NZD/USD

'''


#def run_producer(type_list,year_list):
#    
#    for Type in type_list:      #traverse currency pair
#        for year in year_list:  #traverse year
#            for i in range(1,13):  #traverse month
#                try:
#                    if i < 10:
#                        month = '0' + str(i)
#                    else:
#                        month = str(i)
#
#                    with open('data/{}/DAT_ASCII_{}_T_{}{}.csv'.format(Type,Type,year,month), 'r', newline='', encoding='utf-8-sig') as file:
#                        process_file(file,Type)
#            
#                except Exception as e:
#                    pass
# 
#get all files path under bucket           
def get_key():
    s3 = boto3.resource(service_name='s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name='us-west-2') #open s3 client
    #check how many bucket there are
    #for bucket in s3.buckets.all():
    #    print(bucket.name)
    key_list = [obj.key for page in s3.Bucket(bucket_name).objects.pages() for obj in page]  #get all file path under bucket
    return key_list



def run_producer(type_list,year_list):
    key_list = get_key()
    for Type in type_list:      #traverse currency pair
        for year in year_list:  #traverse year
            for i in range(1,13):  #traverse month
                try:
                    if i < 10:
                        month = '0' + str(i)
                    else:
                        month = str(i)
                        
                    for key in key_list:
                        if Type in key and year in key and month in key:
                            process_file(Type,key)
            
                except Exception as e:
                    #print(e)
                    pass

type_list = ['AUDUSD','AUDCAD','USDCAD','EURUSD','GBPUSD','USDJPY','USDCHF','NZDUSD'] 
year_list = ['2018']

run_producer(type_list,year_list)
