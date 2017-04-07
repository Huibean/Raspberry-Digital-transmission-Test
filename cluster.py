from flask import Flask
import serial
import datetime
import time
from threading import Thread


def receive_function():
    read_frequency = 0.1
    ser = serial.Serial('/dev/ttyS0', '115200', timeout = read_frequency, writeTimeout = 0)
    print("初始化串口...")

    while True:
        data = ser.read(1)
        if (len(data) == 1):
            print(data)

receive_dataThread = Thread( target = receive_function, args = ())
receive_dataThread.start()

app = Flask(__name__)

@app.route("/")

def hello():
    return "Hello World!"

if __name__ == "__main__":
    app.run(host='0.0.0.0')
