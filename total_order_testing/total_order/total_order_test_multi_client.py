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
def get_sqn(loc, sqn):
    while loc.value:
        continue
    loc.value = 1
    print("set the lock")
    lo_sqn = sqn.value
    sqn.value += 1
    print("releasing the lock")
    loc.value = 0
    return lo_sqn
    
def client_1(sqn, loc):
    print("starting client 1")
    MCAST_GRP = '224.1.1.1'
    MCAST_PORT = 5007
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
    while True:
        sqn_ = get_sqn(loc, sqn)
        time_ = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        message = {"id":"clien_1","send_time": time_,"oper": "key-value", "message":{"oper-type": "read", "sqn_no":sqn_}}
        message = json.dumps(message)
        message = str.encode(message)    
        sock.sendto(message, (MCAST_GRP, MCAST_PORT))
        print("client1 sent message with sqn ",sqn_, " and time is" ,time_)
        slp = random.uniform(0.1, 0.3)
        time.sleep(slp)
        
def client_2(sqn, loc):
    MCAST_GRP = '224.1.1.1'
    MCAST_PORT = 5007
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
    while True:
        sqn_ = get_sqn(loc, sqn)
        time_ = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        message = {"id":"clien_2","send_time":time_,"oper": "key-value", "message":{"oper-type": "write", "sqn_no":sqn_}}
        message = json.dumps(message)
        message = str.encode(message)    
        sock.sendto(message, (MCAST_GRP, MCAST_PORT))
        print("client2 sent message with sqn ",sqn_, " and time is" ,time_)
        slp = random.uniform(0.1, 0.3)
        time.sleep(slp)
        

if __name__ == '__main__':
    manager = Manager()
    sqn = manager.Value('i',0)
    loc = manager.Value('i',0)
    cl1 = multiprocessing.Process(target=client_1, args = (sqn, loc))
    cl2 = multiprocessing.Process(target=client_2, args = (sqn, loc))
    cl1.start()
    cl2.start()
    cl1.join()
    cl2.join()
    


    
