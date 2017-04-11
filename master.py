from flask import Flask, render_template, request, redirect, url_for 
import serial
import datetime
import time
import json
from pymongo import MongoClient
from threading import Thread
import yaml
import os

clusters = ['1', '2', '3', '4']

with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

mongodb_url = cfg['mongodb_url']
serial_port = cfg['serial_port']

client = MongoClient(mongodb_url)
db = client['raspberry_transmission_test']
tests = db.tests
records = db.records

def send_function(test_id):
    read_frequency = 0.1
    master = serial.Serial(serial_port, '38400', timeout = read_frequency, writeTimeout = 0)
    master.write(b'9527')
    time.sleep(3)
    master.flushOutput()
    print("初始化主机串口...")
    i = 1
    while True:
        time_now = datetime.datetime.now().strftime('%M:%S.%f')
        data = "0000" + str(test_id) + "-" + str(i) + "-" + time_now + "-"
        for item in range(66 - len(data)):
            data += "x"
        data += "9999"

        master.write(data.encode("UTF-8"))
        time.sleep(0.05)
        i += 1
        print("发送 NO." + str(i) + " " + str(data))
        if i >= 100:
            break
        
    print("测试结束")
    master.close()

app = Flask(__name__, static_folder='public')

@app.route("/", methods = ['GET'])

def index():
    tests = list(db.tests.find())
    tests.reverse()

    print("加载测试结果", tests)

    return render_template('index.html', tests=tests)

@app.route("/get_records/<test_id>", methods = ['GET'])

def get_records(test_id):
    print("处理请求测试数据, 测试ID", test_id)
    data = []
    for cluster_id in clusters:
        cluster_item = { 'name': "Cluster %s"%cluster_id, 'data': [None for i in range(100)]}
        records = list(db.records.find({'test_id': int(test_id), 'cluster_id': int(cluster_id)}))
        for record in records:
            cluster_item['data'][int(record['message_index']) - 1] = float(record['delay'])
        data.append(cluster_item)

    print(data)

    return json.dumps(data)

@app.route("/run_test", methods = ['GET'])

def run_test():
    os.popen("sudo /etc/init.d/ntp restart")
    test_id = len(list(tests.find())) + 1
    title = request.values.get('title')
    print("开始测试...")

    tests.insert_one({"test_id": test_id, "title": title})

    send_function(test_id)

    return redirect(url_for('index'))

@app.route("/upload_record", methods = ['POST'])

def upload_record():
    try:
        test_id = request.args.get('test_id')
        index = request.args.get('index')
        delay = request.args.get('delay')
        cluster_id = request.args.get('cluster_id')
        print("处理请求写入数据, test id: ", test_id, "index: ", index, " delay: ", delay, " cluster_id:", cluster_id)
        records.insert_one({"test_id": test_id, "message_index": index, "delay": delay, "cluster_id": cluster_id})
        return "success"
    except Exception as e:
        raise e
        return "fail"

if __name__ == "__main__":
    app.run(host='0.0.0.0')
