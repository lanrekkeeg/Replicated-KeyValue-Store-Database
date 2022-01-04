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
MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)

def send_message(message):
    message = json.dumps(message)
    message = str.encode(message)    
    sock.sendto(message, (MCAST_GRP, MCAST_PORT))
    
def response():
    """
    """
    muticast_recv = MulticastRec(1)
    print("Starting response ")
    while True:
        data, addr = muticast_recv.sock.recvfrom(1024)
        message = data.decode()
        message = json.loads(message)
        
        if message.get("oper",None) == "response":
            print("Response received for ",message['nodeID']," and response is \n",message['message'],"\n")
            return
            
def client_2(sqn, loc,l):
    print("Starting client 2")
    
    message = {"nodeID":"clien_2","oper": "status", "message":{"status": "sqn"}}
    send_message(message)
    
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


    
