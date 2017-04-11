from flask import Flask
import serial
import datetime
import time
from threading import Thread
import requests
import yaml
import os

with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

cluster_id = cfg['cluster_id'] 

master_server = cfg['master_server']
serial_port = cfg['serial_port']

upload_record_path = master_server + "upload_record"

def time_correct():
    while True:
        os.popen("sudo /etc/init.d/ntp restart")

time_correct_thread = Thread( target = time_correct, args = ())
time_correct_thread.start()

def write_record(test_id, index, delay, cluster_id):
    print("请求写入数据, test id: ", test_id, "index: ", index, " delay: ", delay, "cluster_id: ", cluster_id)
    r = requests.post(upload_record_path, params={"test_id": test_id, "index": index, "delay": delay, "cluster_id": cluster_id})
    print("写入结果", r.status_code, r.content)

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

def receive_function(cluster_id):
    print("初始化串口...")
    read_frequency = 0.1
    cluster = serial.Serial('/dev/ttyAMA0', '38400', timeout = read_frequency, writeTimeout = 0)
    #  cluster = serial.Serial(serial_port, '115200', timeout = read_frequency, writeTimeout = 0)

    cluster.flushInput()

    print("测试就绪!")

    while True:

        data = cluster.read(70)

        if (len(data) == 70):
            print(data)
            later_time = datetime.datetime.now().strftime('%M:%S.%f')
            try:
                test_id, index, former_time, pack_data = data.decode("utf-8").split("-")
                delay = cal_delay(former_time, later_time)

                write_record_thread = Thread( target = write_record, args = (int(test_id), index, delay, cluster_id))
                write_record_thread.start()
            except Exception as e:
                print("异常关闭！")
                cluster.close()
                receive_function(cluster_id)
                raise e
                #  receive_dataThread = Thread( target = receive_function, args = ())
                #  receive_dataThread.start()

receive_function(cluster_id)
