from flask import Flask, render_template, request
import serial
import datetime
import time
import json
import sqlite3
from threading import Thread

database_connection = sqlite3.connect('transmission_test_master.db')
app_c = database_connection.cursor() 

#  try:
    #  app_c.execute('''CREATE TABLE IF NOT EXISTS tests (id integer, delay real, loss real)''')
    #  app_c.execute('''CREATE TABLE IF NOT EXISTS records (test_id integer, index integer, delay real, cluster_id)''')
#  except Exception as e:
    #  pass

def send_function(test_id):
    read_frequency = 0.1
    #  master = serial.Serial('/dev/ttyAMA0', '115200', timeout = read_frequency, writeTimeout = 0)
    master = serial.Serial('/dev/cu.SLAB_USBtoUART', '38400', timeout = read_frequency, writeTimeout = 0)

    master.flushOutput()
    print("初始化主机串口...")
    i = 1
    while True:
        time_now = datetime.datetime.now().strftime('%M:%S.%f')
        data = str(test_id) + "-" + str(i) + "-" + time_now + "-"
        for item in range(70 - len(data)):
            data += "0"

        master.write(data.encode("UTF-8"))
        time.sleep(0.1)
        i += 1
        print("发送 NO." + str(i))
        if i >= 100:
            break
        
    print("测试结束")
    master.close()

app = Flask(__name__, static_folder='public', static_url_path='')
app = Flask(__name__)

@app.route("/", methods = ['GET'])

def index():
    return render_template('index.html')

@app.route("/run_test", methods = ['GET'])

def run_test():
    test_id = len(list(app_c.execute('SELECT * FROM tests'))) + 1

    app_c.execute("INSERT INTO tests VALUES (?,?,?)", (test_id, 0, 0))

    send_dataThread = Thread( target = send_function, args = (str(test_id)))
    send_dataThread.start()
    #  send_function(test_id)
    return json.dumps({"test_id": test_id})

@app.route("/upload_record", methods = ['POST'])

def upload_record():
    print(request.args)
    try:
        test_id = request.args.get('test_id')
        index = request.args.get('index')
        delay = request.args.get('delay')
        cluster_id = request.args.get('cluster_id')
        print("处理请求写入数据, test id: ", test_id, "index: ", index, " delay: ", delay, " cluster_id:", cluster_id)
        app_c.execute("INSERT INTO records VALUES (?,?,?)", (test_id, index, delay, cluster_id))
        return "success"
    except Exception as e:
        return "fail"

if __name__ == "__main__":
    app.run(host='0.0.0.0')
