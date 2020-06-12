import os
import csv
from kafka import KafkaProducer 

def random_forex_generator(): 
num = random.forex(30,1)
return struct.pack('f',num) 


def produce(topic='topic'): 
bootstrap_servers = ['localhost:9092']
topic_name = topic
producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
producer = KafkaProducer()
while True: 
	ack = producer.send(topic_name,random_forex_generator())
	print(ack.get())

if __name__ == "__main__"
random.seed(23)
produce('forex')


