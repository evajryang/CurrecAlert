import os
import sqlites
import csv

def buildingDB():
    conn = sqlite3.connect('db/forex_analysis.db')
    cur = conn.cursor()
    cur.execute("""
        create table forex (
              date_minute varchar(20) NOT NULL PRIMARY KEY ,
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
    
#insert database    
def sql_insert(conn, entities):
    cursorObj = conn.cursor()

    cursorObj.execute("""INSERT INTO forex(date_minute,max_bid_price,min_bid_price,avg_bid_price,max_ask_price,
                                        min_ask_price,avg_ask_price,max_spread,min_spread,avg_spread) 
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", entities)
    conn.commit()

    cursorObj.close()
