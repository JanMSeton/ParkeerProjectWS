# # https://projecthub.arduino.cc/ansh2919/serial-communication-between-python-and-arduino-663756
# import serial
# import time

# arduino = serial.Serial(port='COM4',  baudrate=9600, timeout=.1)


# def write_read(x):
#     arduino.write(bytes(x,  'utf-8'))
#     time.sleep(0.05)
#     data = arduino.readline()
#     return  data


# while True:
#     num = input("Enter a number: ")
#     value  = write_read(num)
#     print(value)

# code AJ

#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json
import serial
from multiprocessing import Process
from http.server import HTTPServer, BaseHTTPRequestHandler
import serial 
import time 

try:
    arduino = serial.Serial('COM4', baudrate=9600, timeout=.1)
except serial.SerialException as e:
    print(f"Error opening serial port: {e}")

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        # message = 'Hello, world!'
        if(arduino.in_waiting >0):
            line = arduino.readline()
            print(line)
            self.wfile.write(bytes(line, "utf8"))
        else:
            self.wfile.write(bytes("No data", "utf8"))
        # self.wfile.write(bytes(message, "utf8"))
def run_server():
    arduino = serial.Serial('COM4', baudrate=9600, timeout=.1)
    print("starting")
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, RequestHandler)
    httpd.serve_forever()
if __name__ == '__main__':
    processes = []
    # for _ in range(4):                         # creating 4 separate processes and saving them into a list
    process = Process(target=run_server)
    processes.append(process)
    process.start()
    for process in processes:
        process.join()
 