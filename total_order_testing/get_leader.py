#!/usr/bin/env python

from logging import Logger
import socket
import struct
import json
import time
import multiprocessing
from multiprocessing import Manager
import random
import datetime
from broad_multi_cast import MulticastSend,MulticastRec
broad_cast_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
broad_cast_sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
broad_cast_sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)


broad_cast_receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
broad_cast_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
broad_cast_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
broad_cast_receiver.bind(("192.168.0.255", 37020))




def send_message(message):
    message = json.dumps(message)
    message = str.encode(message)    
    broad_cast_sender.sendto(message,("192.168.0.255", 37020))
    
def response():
    """
    """
    print("Starting response ")
    while True:
        data, addr = broad_cast_receiver.recvfrom(1024)
        message = data.decode()
        message = json.loads(message)
        
        if message.get("oper",None) == "response":
            print("Response received for ",message['nodeID']," and response is \n",message['message'],"\n")
            
def client_2(sqn, loc,l):
    print("Starting client 2")
    while True:
        message = {"nodeID":"clien_2","oper": "status", "message":{"status": "leader", "bucket_name":"db","content":[1]}}
        send_message(message)
        time.sleep(1)
    
    #slp = random.uniform(0.1, 0.3)
    #time.sleep(slp)
        

if __name__ == '__main__':
    manager = Manager()
    sqn = manager.Value('i',0)
    loc = manager.Value('i',0)
    l = manager.Lock()
    cl2 = multiprocessing.Process(target=client_2, args = (sqn, loc,l))
    resp = multiprocessing.Process(target=response)
    cl2.start()
    resp.start()
    cl2.join()
    resp.join()


    
