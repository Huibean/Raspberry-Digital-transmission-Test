from flask import Flask
import serial
import datetime
import time
import sqlite3
from threading import Thread

database_connection = sqlite3.connect('transmission_test.db')
c = database_connection.cursor() 

try:
    c.execute('''CREATE TABLE test_records (id integer, delay real, loss real)''')
except Exception as e:
    pass

def write_record(c):
    test_id = len(c.execute('SELECT * FROM test_results')) + 1
    c.execute("INSERT INTO test_records VALUES (?,?,?)", (test_id, 0, 0))
    return test_id

def send_function(c):
    read_frequency = 0.1
    #  master = serial.Serial('/dev/ttyS0', '115200', timeout = read_frequency, writeTimeout = 0)
    master = serial.Serial('/dev/cu.wchusbserial14110', '115200', timeout = read_frequency, writeTimeout = 0)
    print("初始化串口...")
    i = 0
    test_id = str(write_record(c))
    while True:
        time = datetime.datetime.now().strftime('%M:%S.%f')
        data = test_id + "-" + time + "-"
        for i in range(70 - len(data)):
            data += "0"

        master.write(data.encode("UTF-8"))
        time.sleep(0.1)
        i += 1
        if i < 1000:
            break
        
    master.close()

send_dataThread = Thread( target = send_function, args = (c))
send_dataThread.start()

app = Flask(__name__)

@app.route("/run_test")

def run_test():
    return "Hello World!"

if __name__ == "__main__":
    app.run(host='0.0.0.0')
