# -*- coding: utf-8 -*-
import os
import json
import pandas as pd
import numpy as np
import prettytable as pt
from datetime import datetime
import time
import sqlite3

import math
import numpy.random as npr
#import matplotlib.pyplot as plt
import time

from kafka import KafkaConsumer
from multiprocessing import Process


 
consumer1 = KafkaConsumer(
   'AUDUSD-csv-data',
       bootstrap_servers=['127.0.0.1:9092'],
       value_deserializer=lambda m: json.loads(m.decode('utf-8')),
       key_deserializer=bytes.decode
    )

consumer2 = KafkaConsumer(
   'AUDCAD-csv-data',
       bootstrap_servers=['127.0.0.1:9092'],
       value_deserializer=lambda m: json.loads(m.decode('utf-8')),
       key_deserializer=bytes.decode
    )

consumer3 = KafkaConsumer(
   'USDCAD-csv-data',
       bootstrap_servers=['127.0.0.1:9092'],
       value_deserializer=lambda m: json.loads(m.decode('utf-8')),
       key_deserializer=bytes.decode
    )

consumer4 = KafkaConsumer(
   'EURUSD-csv-data',
       bootstrap_servers=['127.0.0.1:9092'],
       value_deserializer=lambda m: json.loads(m.decode('utf-8')),
       key_deserializer=bytes.decode
    )

consumer5 = KafkaConsumer(
   'GBPUSD-csv-data',
       bootstrap_servers=['127.0.0.1:9092'],
       value_deserializer=lambda m: json.loads(m.decode('utf-8')),
       key_deserializer=bytes.decode
    )

consumer6 = KafkaConsumer(
   'USDJPY-csv-data',
       bootstrap_servers=['127.0.0.1:9092'],
       value_deserializer=lambda m: json.loads(m.decode('utf-8')),
       key_deserializer=bytes.decode
    )

consumer7 = KafkaConsumer(
   'USDCHF-csv-data',
       bootstrap_servers=['127.0.0.1:9092'],
       value_deserializer=lambda m: json.loads(m.decode('utf-8')),
       key_deserializer=bytes.decode
    )

consumer8 = KafkaConsumer(
   'NZDUSD-csv-data',
       bootstrap_servers=['127.0.0.1:9092'],
       value_deserializer=lambda m: json.loads(m.decode('utf-8')),
       key_deserializer=bytes.decode
    )




 
def separate_date_timestamp(msg_value):
    try:
        date_timestamp = time.strptime(msg_value['DataTime Stamp'],"%Y%m%d %H%M%S%f")
        msg_value['date'] = msg_value['DataTime Stamp'].split(' ')[0]
        msg_value['timestamp'] = str(int(time.mktime(date_timestamp)))
    except Exception as e:
        print(e)
        msg_value['date'] = ''
        msg_value['timestamp'] = ''
    return msg_value

 
def calculate_spread(msg_value):
    try:
        bid = float(msg_value['Bid Quote'])
        ask = float(msg_value['Ask Quote'])
        msg_value['spread'] = str(format((bid - ask),'.8f'))
    except Exception as e:
        msg_value['spread'] = ''
    return msg_value



def get_hour(data_daily):
    res = []
    for d in data_daily:
        d['hour'] = d['DataTime Stamp'][9:11]
        res.append(d)
    return res
    


def _trading_hour_daily(data_daily):
    data_daily = get_hour(data_daily)
    spread = [d['spread'] for d in data_daily]
    lowest_spread = min(spread) 
    data_lowest_spread = [d for d in data_daily if d['spread']==lowest_spread]
    

    len_data_hour = []
    for i in range(24):
        if len(str(i))<2:
            i = '0'+ str(i)
        else:
            i = str(i)
        len_data_hour.append(len([dlp for dlp in data_lowest_spread if dlp['hour'] == i ]))
              
    return len_data_hour.index(max(len_data_hour)) 
    


def max_min_avg(data_daily):
    bid_price = [float(d['Bid Quote']) for d in data_daily]
    ask_price = [float(d['Ask Quote']) for d in data_daily]
    spread = [float(d['spread']) for d in data_daily]
    
    max_bid_price = max(bid_price)
    min_bid_price = min(bid_price)
    avg_bid_price = np.mean(bid_price)
    
    max_ask_price = max(ask_price)
    min_ask_price = min(ask_price)
    avg_ask_price = np.mean(ask_price)

    max_spread = max(spread)
    min_spread = min(spread)
    avg_spread = np.mean(spread)

    return max_bid_price,min_bid_price,avg_bid_price,max_ask_price,min_ask_price,avg_ask_price,max_spread,min_spread,avg_spread
    

def simulation_Geometric_Brownian_motion(S0):
    T = 2.0
    r = 0.05
    sigma = 0.25

  
    I = 1
   
    M = 20
    dt = T / M
    S = np.zeros((M+1, I))
    S[0] = S0
    for t in range(1, M+1):
        S[t] = S[t-1] * np.exp((r - 0.5 * sigma ** 2) * dt +
                               sigma * math.sqrt(dt) * npr.standard_normal(I))
    ST = S[-1]

    #plt.hist(ST,bins=50, alpha=0.5)
    #plt.xlabel('index level')
    #plt.ylabel('frequency')
    return ST
    
    
def print_d(msg_value):
    tb = pt.PrettyTable()
    tb.field_names = ['column','value']
    msg_name = list(msg_value.keys())
    for mn in msg_name:
        tb.add_row([mn,msg_value[mn]])
    print()
    print(tb)
    

def get_date(msg_value):
    date = msg_value['DataTime Stamp'][:8]
    return date

    
def get_date_minute(msg_value):
    date_minute = msg_value['DataTime Stamp'][:13]
    return date_minute


def add_date_minute(msg_value):
    msg_value['date_minute'] = get_date_minute(msg_value)
    return msg_value
    

def buildingDB():
    conn = sqlite3.connect('db/forex_analysis.db')
    cur = conn.cursor()
    cur.execute("""
        create table forex (
              date_minute varchar(20) NOT NULL  ,
              max_bid_price varchar(16) ,
              min_bid_price varchar(16),
              avg_bid_price varchar(16) ,
              max_ask_price varchar(16) ,
              min_ask_price varchar(16) ,
              avg_ask_price varchar(16),
              max_spread varchar(16),
              min_spread varchar(16),
              avg_spread varchar(16)
          );
        """)
    cur.close()
    
    
def sql_insert(conn, entities):
    cursorObj = conn.cursor()

    cursorObj.execute("""INSERT INTO forex(date_minute,max_bid_price,min_bid_price,avg_bid_price,max_ask_price,
                                        min_ask_price,avg_ask_price,max_spread,min_spread,avg_spread) 
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", entities)
    conn.commit()

    cursorObj.close()


def alert_reminder(date,history_spread,current_spread):
    if history_spread > current_spread:
        with open('lowest_spread_record.csv','a',encoding='utf-8') as f:
            print('{} lowestspread'.format(date))
            print('{} lowestspread'.format(date),file=f)
        history_spread = current_spread 

        time.sleep(5)  

    return history_spread
        
 


def trans_date(date):
    date_list = list(date)
    date_list.insert(11, ':')
    date_list.insert(14, ':')
    date_list.insert(17, '.')
    date = ''.join(date_list)
    return date

    







if not os.path.exists('db/forex_analysis.db'):
    buildingDB() 
else:
    os.remove('db/forex_analysis.db')
    buildingDB() 


    

def run_consumer(consumer):
    date_minute = ''
    data_min = []  
    
    date_daily = ''
    data_daily = []  
    
    history_spread = 100
    
    
    
    conn = sqlite3.connect('db/forex_analysis.db')

    for msg in consumer:
        try:
            
            msg_value = msg.value
            msg_topic = msg.topic
            
            if not date_minute:
                date_minute = get_date_minute(msg_value)
           
            if not date_daily:
                date_daily = get_date(msg_value)
    
    
            msg_value = separate_date_timestamp(msg_value)
            msg_value = calculate_spread(msg_value)
            msg_value = add_date_minute(msg_value)
            

     

            if float(msg_value['spread']) < history_spread:
                msg_value['current_lowest_spread'] = msg_value['spread']
            else:
                msg_value['current_lowest_spread'] = history_spread
#            
            
            data_min.append(msg_value) 
            data_daily.append(msg_value) 
    
    
    
            if msg_value['date_minute'] != date_minute:
                
                print('####### {} Analysis Result {} #####'.format(msg_topic.split('-')[0],date_minute))
                data_min.pop(-1)
                max_bid_price,min_bid_price,avg_bid_price,max_ask_price,min_ask_price,avg_ask_price,max_spread,min_spread,avg_spread = max_min_avg(data_min)
                #print('best_daily_trading_hour:',trading_hour_daily)
                print('max_bid_price:',max_bid_price)
                print('min_bid_price:',min_bid_price)
                print('avg_bid_price:',avg_bid_price)
                print('max_ask_price:',max_ask_price)
                print('min_ask_price:',min_ask_price)
                print('avg_ask_price:',avg_ask_price)
                print('max_spread:',max_spread)
                print('min_spread:',min_spread)
                print('avg_spread:',avg_spread)
                print()
                
                
                entities = (date_minute,max_bid_price,min_bid_price,avg_bid_price,
                            max_ask_price,min_ask_price,avg_ask_price,
                            max_spread,min_spread,avg_spread)
    
                sql_insert(conn, entities)
                
                
                
                history_spread = alert_reminder(date_minute,history_spread,min_spread)
                msg_value['current_lowest_spread'] = history_spread
                
                data_min = [msg_value] 
                date_minute = msg_value['date_minute']
            
                
                
             
            if msg_value['date'] != date_daily: 
                data_daily.pop(-1)
                
                max_bid_price_daily,min_bid_price_daily,avg_bid_price_daily, \
                    max_ask_price_daily,min_ask_price_daily,avg_ask_price_daily, \
                    max_spread_daily,min_spread_daily,avg_spread_daily = max_min_avg(data_daily)
    
                print('{} day lowestspreadis：{}'.format(date_daily,min_spread_daily))
               
                history_spread = min_spread_daily
                msg_value['current_lowest_spread'] = history_spread
#                
                history_spread = 100
                print('historicalspreadafterupdate：{}'.format(history_spread))
                
                ## 
                df_daily = pd.DataFrame(data_daily)
                df_daily['Date'] = df_daily['DataTime Stamp'].apply(trans_date)
                df_daily = df_daily.rename(columns={'Ask Quote':'Ask','Bid Quote':'Bid'})
                del df_daily['date_minute'],df_daily['DataTime Stamp'],df_daily['timestamp']
                df_daily = df_daily[['TYPE','Date', 'Bid','Ask', 'VoLUME', 'date', 'spread','current_lowest_spread']]
                del df_daily['VoLUME'],df_daily['date'],df_daily['spread']
#                df_daily['Bid'] = df_daily['Bid'].apply(lambda x :float(x)*100)
#                df_daily['Ask'] = df_daily['Ask'].apply(lambda x: float(x)*100)
                df_daily.to_csv('result/{}.csv'.format(msg_topic.split('-')[0]),index=False,encoding='utf-8')
                
                
                
                data_daily = [msg_value]
                date_daily = msg_value['date']
    
                time.sleep(10)  
     

             
        except Exception as e:
            print(e)
            pass
            


if __name__ == "__main__": 
    consumer_list = [consumer1,consumer2,consumer3,consumer4,consumer5,consumer6,consumer7,consumer8] 
    for consumer in consumer_list:
        proc = Process(target=run_consumer, args=(consumer,))
        proc.start()

#run_consumer(consumer1)

