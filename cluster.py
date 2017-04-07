import serial
import datetime
import time
import sqlite3
from threading import Thread

database_connection = sqlite3.connect('transmission_test.db')
serial_c = database_connection.cursor() 

try:
    serial_c.execute('''CREATE TABLE test_results (test_id integer, delay real, date text)''')
except Exception as e:
    pass

def write_record(c, test_id, delay):
    c.execute("INSERT INTO test_results VALUES (?,?,?)", (test_id, delay, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))

def cal_delay(former_time, later_time):
    former_m, former_s = map(lambda item: float(item), former_time.split(":")) 
    later_m, later_s = map(lambda item: float(item), later_time.split(":"))
    delay = 0.00
    if former_m == later_m:
        delay = later_s - former_s
    elif later_m > former_m:
        delay = (later_m - former_m) * 60.00 + later_s - former_s
    elif later_m < former_m:
        delay = (later_m - former_m + 60) * 60.00 + later_s - former_s

    return delay

def receive_function(c):
    read_frequency = 0.1
    cluster = serial.Serial('/dev/ttyS0', '115200', timeout = read_frequency, writeTimeout = 0)
    print("初始化串口...")

    while True:
        data = cluster.read(70)
        if (len(data) == 70):
            print(data)
            later_time = datetime.datetime.now().strftime('%M:%S.%f')
            test_id, former_time, pack_data = data.decode("utf-8").split("-")
            delay = cal_delay(former_time, later_time)

            write_thread = Thread( target = write_record, args = (int(test_data), delay))
            write_thread.start()

receive_dataThread = Thread( target = receive_function, args = (serial_c))
receive_dataThread.start()
