# -*- coding: utf-8 -*-
import csv
import time
from kafka import KafkaProducer
from os import path
from multiprocessing import Process

import boto3
import json
import lazyreader
import schedule


#class CsvEngine:
#    def __init__(self, file):
#        self.csv_data = csv.reader(file)
#
#    def process_csv(self, f,Type):
#

### read CSV line by line

#        count = 0
#        for line in self.csv_data:
#            count += 1
#            line = {'DataTime Stamp':line[0],'Bid Quote':line[1],'Ask Quote':line[2],'VoLUME':line[3],'TYPE':Type}
#            f(line)
#            print(line)
#            #time.sleep(0.1)
#        return count


aws_access_key_id = '***********'    #aws id
aws_secret_access_key = '**********'   #aws key
bucket_name = 'forexdata2000-2018'  #bucket

class CsvEngine:
    def __init__(self):
        self.s3 = boto3.client('s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
        
    def process_csv(self, f,Type,key):
        obj = self.s3.get_object(Bucket=bucket_name, Key=key)
        count = 0
        for line in lazyreader.lazyread(obj["Body"], delimiter=b'\n'):
            line = line.decode().replace('\n','').split(',')
            count += 1
            line = {'DataTime Stamp':line[0],'Bid Quote':line[2],'Ask Quote':line[1],'VoLUME':line[3],'TYPE':Type}
            f(line)
            print(line)
            #time.sleep(0.1)
        return count
    
    
#csv2kafka producer
class KafkaEngine:
    def __init__(self,Type):
        self.producer = KafkaProducer(bootstrap_servers=['127.0.0.1:9092'],value_serializer=lambda m: json.dumps(m).encode('utf-8'),
                        key_serializer=str.encode)
        self.Type = Type

    def send_to_csv_data_topic(self, key, data):
        future = self.producer.send('{}-csv-data'.format(self.Type), key=key, value=data)
        record_metadata = future.get(timeout=10)

    def close(self):
        self.producer.flush(100)
        self.producer.close(100)




def process_file(Type,key):
    kafka = KafkaEngine(Type)
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
#    for Type in type_list:      #for loop currency pair
#        for year in year_list:  #for loop year
#            for i in range(1,13):  #forloop month
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
#Receive all paths of files under the bucket
def get_key():
    s3 = boto3.resource(service_name='s3', aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key, region_name='us-west-2') #open S3 client port
    #check the number of bucket
    #for bucket in s3.buckets.all():
    #    print(bucket.name)
    key_list = [obj.key for page in s3.Bucket(bucket_name).objects.pages() for obj in page]  #receive all the paths of files under the bucket
    return key_list



#def run_producer(type_list,year_list):
#    key_list = get_key()
#    for Type in type_list:      #forloop currency pair
#        for year in year_list:  #forloop year
#            for i in range(1,13):  #forloop month
#                try:
#                    if i < 10:
#                        month = '0' + str(i)
#                    else:
#                        month = str(i)
#                        
#                    for key in key_list:
#                        if Type in key and year in key and month in key:
#                            process_file(Type,key)
#            
#                except Exception as e:
#                    #print(e)
#                    pass
#
#type_list = ['AUDUSD','AUDCAD','USDCAD','EURUSD','GBPUSD','USDJPY','USDCHF','NZDUSD'] 
#year_list = ['2018']
#
#run_producer(type_list,year_list)
    


def run_producer(type_list,year_list):
    key_list = get_key()
    for Type in type_list:      #forloop currency pairs
        for year in year_list:  #forloop year
            for i in range(1,13):  #forloop month
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


if __name__ == "__main__":  
    type_list = ['AUDUSD','AUDCAD','USDCAD','EURUSD','GBPUSD','USDJPY','USDCHF','NZDUSD'] 
    year_list = ['2018']
    

    for Type in type_list:
        proc = Process(target=run_producer, args=([Type],year_list))
        proc.start()
    
    '''
    schedule.every(5).hour.do(job)

    while True:
        schedule.run_pending()  
        time.sleep(1)

    '''


