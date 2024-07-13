# data acqusition module 

import csv
from os import name
import pandas as pd 
from init import *
import sqlite3
from sqlite3 import Error
from datetime import datetime
import time as tm
from icecream import ic as ic2
import matplotlib.pyplot as plt
import random


def time_format():
    return f'{datetime.now()}  data acq|> '

ic2.configureOutput(prefix=time_format)



def create_connection(db_file=db_name):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        pp = ('Conected to version: '+ sqlite3.version)
        ic2(pp)
        return conn
    except Error as e:
        ic2(e)

    return conn


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        ic2(e)


def init_db(database):
    # database = r"data\homedata.db"    
    tables = [
    """ CREATE TABLE IF NOT EXISTS `data` (
	`name`	TEXT NOT NULL,
	`timestamp`	TEXT NOT NULL,
	`value`	TEXT NOT NULL,
	FOREIGN KEY(`value`) REFERENCES `iot_devices`(`name`)
    );""",
    """CREATE TABLE IF NOT EXISTS `iot_devices` (
	`sys_id`	INTEGER PRIMARY KEY,
	`name`	TEXT NOT NULL UNIQUE,
	`status`	TEXT,
    `units`	TEXT,
	`last_updated`	TEXT NOT NULL,
	`update_interval`	INTEGER NOT NULL,
	`address`	TEXT,
	`building`	TEXT,
	`room`	TEXT,
	`placed`	TEXT,
	`dev_type`	TEXT NOT NULL,
	`enabled`	INTEGER,    
	`state`	TEXT,
	`mode`	TEXT,
	`fan`	TEXT,
	`temperature`	REAL,
	`dev_pub_topic`	TEXT NOT NULL,
    `dev_sub_topic`	TEXT NOT NULL,
    `special`	TEXT		
    ); """    
    ]
    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        # create tables
        for table in tables:
            create_table(conn, table)
        conn.close()            
    else:
        ic2("Error! cannot create the database connection.")

def csv_acq_data(table_name):
        conn= create_connection(db_name)        
        try:
            if db_init:                
                data = pd.read_csv("data/homedata.csv")
                data.to_sql(table_name, conn, if_exists='append', index=False)                       
            else:
                data = pd.read_sql_query("SELECT * FROM "+table_name, conn)
        except Error as e:
            ic2(e)
        finally:    
            if conn:
                conn.close()    

def create_IOT_dev(name, status, units, last_updated, update_interval, address, building, room, placed, dev_type, enabled, state, mode, fan, temperature, dev_pub_topic, dev_sub_topic, special):
    """
    Create a new IOT device into the iot_devices table
    :param conn:
    :param :
    :return: sys_id
    """
    sql = ''' INSERT INTO iot_devices(name, status, units, last_updated, update_interval, address, building, room, placed, dev_type, enabled, state, mode, fan, temperature, dev_pub_topic, dev_sub_topic, special)
              VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) '''
    conn = create_connection()
    if conn is not None:
        cur = conn.cursor()
        cur.execute(sql, [name, status, units, last_updated, update_interval, address, building, room, placed, dev_type, enabled, state, mode, fan, temperature, dev_pub_topic, dev_sub_topic, special])
        conn.commit()
        re = cur.lastrowid
        conn.close()
        return re
    else:
        ic2("Error! cannot create the database connection.")    

def timestamp():
    return str(datetime.fromtimestamp(datetime.timestamp(datetime.now()))).split('.')[0]
    

def add_IOT_data(name, updated, value):
    """
    Add new IOT device data into the data table
    :param conn:
    :param :
    :return: last row id
    """
    sql = ''' INSERT INTO data(name, timestamp, value)
              VALUES(?,?,?) '''
    conn = create_connection()
    if conn is not None:
        cur = conn.cursor()
        cur.execute(sql, [name, updated, value])
        conn.commit()
        re = cur.lastrowid
        conn.close()
        return re
    else:
        ic2("Error! cannot create the database connection.")        

def read_IOT_data(table, name):
    """
    Query tasks by name
    :param conn: the Connection object
    :param name:
    :return: selected by name rows list
    """
    
    conn = create_connection()
    if conn is not None:
        cur = conn.cursor()        
        cur.execute("SELECT * FROM " + table +" WHERE name=?", (name,))
        rows = cur.fetchall()   
        return rows
    else:
        ic2("Error! cannot create the database connection.")   

def update_IOT_dev(tem_p):
    """
    update temperature of a IOT device by name
    :param conn:
    :param update:
    :return: project id
    """
    sql = ''' UPDATE iot_devices SET temperature = ?, special = 'changed' WHERE name = ?'''
    conn = create_connection()
    if conn is not None:
        cur = conn.cursor()
        cur.execute(sql, tem_p)
        conn.commit()
        conn.close()        
    else:
        ic2("Error! cannot create the database connection.") 

def update_IOT_status(iot_dev):
    """
    update temperature of a IOT device by name
    :param conn:
    :param update:
    :return: project id
    """
    sql = ''' UPDATE iot_devices SET special = 'done' WHERE sys_id = ?'''
    conn = create_connection()
    if conn is not None:
        cur = conn.cursor()
        cur.execute(sql, (int(iot_dev),))
        conn.commit()
        conn.close()        
    else:
        ic2("Error! cannot create the database connection.") 

def check_changes(table):
    """
    update temperature of a IOT device by name
    :param conn:
    :param update:
    :return: 
    """
    conn = create_connection()
    if conn is not None:
        cur = conn.cursor()        
        cur.execute("SELECT * FROM " + table +" WHERE special=?", ('changed',))
        rows = cur.fetchall()   
        return rows
    else:
        ic2("Error! cannot create the database connection.")      

def fetch_table_data_into_df(table_name, conn, filter):
    return pd.read_sql_query("SELECT * from " + table_name +" WHERE `name` LIKE "+ "'"+ filter+"'", conn)

def filter_by_date(table_name,start_date,end_date, meter):
    conn = create_connection()
    if conn is not None:
        cur = conn.cursor()                
        cur.execute("SELECT * FROM " + table_name +" WHERE `name` LIKE '"+ meter +"' AND timestamp BETWEEN '"+ start_date +"' AND '"+ end_date +"'")
        rows = cur.fetchall()   
        return rows
    else:
        ic2("Error! cannot create the database connection.")     

def fetch_data(database,table_name, filter):
    TABLE_NAME = table_name    
    conn = create_connection(database)
    with conn:        
        return fetch_table_data_into_df(TABLE_NAME, conn,filter)
        
def show_graph(meter, date):
    df = fetch_data(db_name,'data', meter)       
    #df.timestamp=pd.to_numeric(df.timestamp)
    df.value=pd.to_numeric(df.value)
    ic2(len(df.value))
    ic2(df.value[len(df.value)-1])
    ic2(max(df.value))
    ic2(df.timestamp)
    df.plot(x='timestamp',y='value')    
    # fig, axes = plt.subplots (2,1)
    # # Draw a horizontal bar graph and a vertical bar graph
    # df.plot.bar (ax = axes [0])
    # df.plot.barh (ax = axes [1])
    plt.show()


if __name__ == '__main__':
    if db_init:
        init_db(db_name)
        # insertion init IOT dataset    
        numb =create_IOT_dev('DHT-1', 'on', 'celcius', timestamp(), 300, 'address', 'building', 'room', 'placed', 'detector', 'enabled', 'state', 'mode', 'fan', 'temperature', comm_topic+'DHT-1/pub', comm_topic+'DHT-1/sub', 'done')
        numb =create_IOT_dev('DHT-2', 'on', 'celcius', timestamp(), 300, 'address', 'building', 'room', 'placed', 'detector', 'enabled', 'state', 'mode', 'fan', 'temperature', comm_topic+'DHT-2/pub', comm_topic+'DHT-2/sub', 'done')
        numb =create_IOT_dev('DHT-3', 'on', 'celcius', timestamp(), 300, 'address', 'building', 'room', 'placed', 'detector', 'enabled', 'state', 'mode', 'fan', 'temperature', comm_topic+'DHT-3/pub', comm_topic+'DHT-3/sub', 'done')
        numb =create_IOT_dev('DHT-4', 'on', 'celcius', timestamp(), 300, 'address', 'building', 'room', 'placed', 'detector', 'enabled', 'state', 'mode', 'fan', 'temperature', comm_topic+'DHT-4/pub', comm_topic+'DHT-4/sub', 'done')
        
        # add initial row data to all IOT devices:

        rez_dht1 = filter_by_date('data', '2021-05-16', '2021-05-18', 'DHT-1')
        rez_dht2 = filter_by_date('data', '2021-05-16', '2021-05-18', 'DHT-2')
        
        temperature_dht1 = []  
        timenow_dht1 = []

        for row in rez_dht1:
            timenow_dht1.append(row[1])
            temperature_dht1.append("{:.2f}".format(float(row[2])))

        plt.plot_date(timenow_dht1, temperature_dht1, '-', label='DHT-1')

        # Plotting DHT-2 temperature data
        temperature_dht2 = []  
        timenow_dht2 = []

        for row in rez_dht2:
            timenow_dht2.append(row[1])
            temperature_dht2.append("{:.2f}".format(float(row[2])))

        plt.plot_date(timenow_dht2, temperature_dht2, '-', label='DHT-2')

        plt.legend()
        plt.xlabel('Timestamp')
        plt.ylabel('Temperature (°C)')
        plt.title('Temperature Data for DHT-1 and DHT-2')
        plt.show()