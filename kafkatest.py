import os
import csv
import pandas as pd
import glob

path = r'Forexdata' #path need to be fixed
all_files = glob.glob(path + "/*.csv")

li = []

for filename in all_files:
    df = pd.read_csv(filename, index_col=None, header=0)
    li.append(df)

frame = pd.concat(li, axis=0, ignore_index=True)


def produce(topic='topic'): 
bootstrap_servers = ['localhost:9092']
topic_name = topic
producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
producer = KafkaProducer()
	print(ack.get())


if __name__ == '__main__':
    main()


