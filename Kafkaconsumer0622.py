#!/usr/bin/env python
# coding: utf-8


import json
import pandas as pd
import numpy as np
import prettytable as pt
from datetime import datetime
import time
import math
import numpy.random as npr
#import matplotlib.pyplot as plt


from kafka import KafkaConsumer
consumer = KafkaConsumer(
   'csv-data',
       bootstrap_servers=['127.0.0.1:9092'],
       value_deserializer=lambda m: json.loads(m.decode('utf-8')),
       key_deserializer=bytes.decode
    )

#separate the date and timestamp to two columns 
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

#Calculate spread= Bid price- ask price 
def calculate_spread(msg_value):
    try:
        bid = float(msg_value['Bid Quote'])
        ask = float(msg_value['Ask Quote'])
        msg_value['spread'] = str(format((bid - ask),'.6f'))
    except Exception as e:
        msg_value['spread'] = ''
    return msg_value


#get hour
def get_hour(data_daily):
    res = []
    for d in data_daily:
        d['hour'] = d['DataTime Stamp'][9:11]
        res.append(d)
    return res
    

#Find the high frequency-trading hour that has the lowest spread in the data 
def _trading_hour_daily(data_daily):
    data_daily = get_hour(data_daily)
    spread = [d['spread'] for d in data_daily]
    lowest_spread = min(spread) 
    data_lowest_spread = [d for d in data_daily if d['spread']==lowest_spread]
    
    #calculate every hour's data
    len_data_hour = []
    for i in range(24):
        if len(str(i))<2:
            i = '0'+ str(i)
        else:
            i = str(i)
        len_data_hour.append(len([dlp for dlp in data_lowest_spread if dlp['hour'] == i ]))
              
    return len_data_hour.index(max(len_data_hour)) 
    

# calculate max, min, avg of ‘bid price’, ‘ask price’ and spread separately
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
    
#simulation  Geometric Brownian motion
def simulation_Geometric_Brownian_motion(S0):
    T = 2.0
    r = 0.05
    sigma = 0.25

    # simulation loops
    I = 1
    # simulation interval
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

    

    
date = ''
data_daily = [] 

for msg in consumer:
    try:
        
    

        msg_value = msg.value
        if not date:
            date = get_date(msg_value)
        
        msg_value = separate_date_timestamp(msg_value)
        msg_value = calculate_spread(msg_value)
        
        
        data_daily.append(msg_value)
        if msg_value['date'] != date:
            print('#######analysis {} #####'.format(date))
            data_daily.pop(-1)
            #Daily statistics
            trading_hour_daily = _trading_hour_daily(data_daily) #trading_hour_daily
            max_bid_price,min_bid_price,avg_bid_price,max_ask_price,min_ask_price,avg_ask_price,max_spread,min_spread,avg_spread = max_min_avg(data_daily)
            print('trading_hour_daily:',trading_hour_daily)
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
            
            year = msg_value['date'][:4] #year
            Type = msg_value['TYPE'] #type
            with open('result/{}_{}_result.csv'.format(year,Type),'a',encoding='utf-8') as f:
                f.write(date)  #data day
                f.write(',')
                f.write(str(trading_hour_daily))  
                f.write(',')

                f.write(str(max_bid_price)) 
                f.write(',') 
                f.write(str(min_bid_price))
                f.write(',') 
                f.write(str(avg_bid_price)) 
                f.write(',') 

                f.write(str(max_ask_price)) 
                f.write(',') 
                f.write(str(min_ask_price)) 
                f.write(',') 
                f.write(str(avg_ask_price)) 
                f.write(',') 

                f.write(str(max_spread)) 
                f.write(',') 
                f.write(str(min_spread)) 
                f.write(',') 
                f.write(str(avg_spread)) 
                f.write('\n') 

            data_daily = [msg_value]
            date = msg_value['date']
        
        #simulate the real-time data
        real_time_bid_price = simulation_Geometric_Brownian_motion(msg_value['Bid Quote'])
        real_time_ask_price = simulation_Geometric_Brownian_motion(msg_value['Ask Quote'])
        real_time_spread = simulation_Geometric_Brownian_motion(msg_value['spread'])
        #print(real_time_bid_price)

         
        #print_d(msg_value)
    except Exception as e:
        pass
        






