from flask import Flask
import serial
import datetime
import time
from threading import Thread
from pymongo import MongoClient
import requests
import yaml
import os
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.OUT)
p = GPIO.PWM(26, 0.5)

with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

cluster_id = cfg['cluster_id'] 

master_server = cfg['master_server']
serial_port = cfg['serial_port']

mongodb_url = cfg['mongodb_url']
client = MongoClient(mongodb_url)
db = client['raspberry_transmission_test']
tests = db.tests
records = db.records

upload_record_path = master_server + "upload_record"

def write_record(test_id, index, delay, cluster_id):
    try:
        print("处理请求写入数据, test id: ", test_id, "index: ", index, " delay: ", delay, " cluster_id:", cluster_id)
        records.insert_one({"test_id": test_id, "message_index": index, "delay": delay, "cluster_id": cluster_id})
    except Exception as e:
        raise e

def write_records(records_to_insert):
    try:
        print("处理请求写入数据: ", records_to_insert)
        records.insert_many(records_to_insert)
    except Exception as e:
        raise e

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

class DataBuffer(object):

    def __init__(self):
        self.head = b''
        self.content = b''
        self.end = b''

    def clear(self):
        self.head = b''
        self.content = b''
        self.end = b''

    def head_correct(self):
        return self.head == b'0000'
    
    def is_end(self):
        return self.end == b'9999'
        

def receive_function(cluster_id):
    print("初始化串口...")
    read_frequency = 0.05
    cluster = serial.Serial('/dev/ttyAMA0', '38400', timeout = read_frequency, writeTimeout = 0)

    cluster.flushInput()

    while True:
        confirm_test_message = cluster.read(4)

        if confirm_test_message == b'9527':
            print("接受到确认数据:", confirm_test_message)
            print("测试就绪!")
            cluster.flushInput()
            system_delay = 0.0

            try:
                os.popen("sudo /etc/init.d/ntp restart")
                result = os.popen("ntpq -p").read()
                system_offset = float(result.split()[-2])   
                print("系统时钟延迟: %s ms"%system_offset)
                system_delay = system_offset * 0.001
            except Exception as e:
                raise e

            idle_count = 0

            data_buffer = DataBuffer()
            records_to_insert = []

            while True:
                data = cluster.read()

                if len(data) == 0:
                    idle_count += 1
                    if idle_count > 100:
                        print("处理请求写入数据: ", records_to_insert)
                        try:
                            db.records.insert_many(records_to_insert)
                            print("写入数据完成")
                        except Exception as e:
                            raise e

                        print("无数据接收，进入休眠...")
                        idle_count = 0
                        break

                if len(data_buffer.head) < 4:
                    p.start(1)
                    data_buffer.head += data
                    data_buffer.content = b''
                    data_buffer.end = b''
                elif data_buffer.head_correct():
                    if len(data_buffer.content) < 62:
                        data_buffer.content += data
                    elif len(data_buffer.content) == 62:
                        if len(data_buffer.end) < 4:
                            data_buffer.end += data
                        elif data_buffer.is_end():
                            later_time = datetime.datetime.now().strftime('%M:%S.%f')
                            p.stop()
                            GPIO.cleanup()
                            print("confirm head:", data_buffer.head)
                            print("confirm content:", data_buffer.content)
                            print("confirm end:", data_buffer.end)
                            try:
                                test_id, index, former_time, pack_data = data_buffer.content.decode("utf-8").split("-")
                                delay = cal_delay(former_time, later_time) + system_delay

                                records_to_insert.append({"test_id": int(test_id), "message_index": int(index), "delay": delay, "cluster_id": int(cluster_id)})

                                #  write_record_thread = Thread( target = write_record, args = (int(test_id), index, delay, cluster_id))
                                #  write_record_thread.start()
                                data_buffer.clear()
                                data_buffer.head += data
                            except Exception as e:
                                print("异常关闭！")
                                cluster.close()
                                receive_function(cluster_id)
                                raise e
                        else:
                            data_buffer.clear()
                    else:
                        data_buffer.clear()
                else:
                    data_buffer.clear()

receive_function(cluster_id)
