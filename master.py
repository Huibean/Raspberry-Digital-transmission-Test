from flask import Flask
import serial
import datetime
import time
import sqlite3
from threading import Thread

database_connection = sqlite3.connect('transmission_test_master.db')
app_c = database_connection.cursor() 

try:
    app_c.execute('''CREATE TABLE test_records (id integer, delay real, loss real)''')
except Exception as e:
    pass

def send_function(test_id):
    read_frequency = 0.1
    #  master = serial.Serial('/dev/ttyS0', '115200', timeout = read_frequency, writeTimeout = 0)
    master = serial.Serial('/dev/cu.wchusbserial14110', '115200', timeout = read_frequency, writeTimeout = 0)
    print("初始化主机串口...")
    i = 0
    while True:
        time_now = datetime.datetime.now().strftime('%M:%S.%f')
        data = str(test_id) + "-" + time_now + "-"
        for i in range(70 - len(data)):
            data += "0"

        master.write(data.encode("UTF-8"))
        time.sleep(0.1)
        i += 1
        if i < 1000:
            break
        
    master.close()

app = Flask(__name__)

@app.route("/run_test", methods = ['GET'])

def run_test():
    test_id = len(list(app_c.execute('SELECT * FROM test_records'))) + 1

    app_c.execute("INSERT INTO test_records VALUES (?,?,?)", (test_id, 0, 0))

    #  send_dataThread = Thread( target = send_function, args = (test_id))
    #  send_dataThread.start()
    send_function(test_id)
    return "Hello World!"

if __name__ == "__main__":
    app.run(host='0.0.0.0')
