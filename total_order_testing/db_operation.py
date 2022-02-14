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

def get_sqn(loc, sqn,lock):
    lock.acquire()
    lo_sqn = sqn.value
    sqn.value += 1
    lock.release()
    '''
    while loc.value:
        continue
    loc.value = 1
    #print("set the lock")
    lo_sqn = sqn.value
    sqn.value += 1
    #print("releasing the lock")
    loc.value = 0
    '''
    return lo_sqn
def send_message(message,sqn, time_, client):
    message = json.dumps(message)
    message = str.encode(message)    
    sock.sendto(message, (MCAST_GRP, MCAST_PORT))
    print(client," sent message with sqn ",sqn, " and time is" ,time_)

def get_time():
    """
    will return time in UTC with string format
    """
    tm = datetime.utcnow().strftime("%m/%d/%Y  %H:%M:%S.%f")
    return tm
def client_1(sqn, loc,l):
    print("starting client 1")
    
    sqn_ = get_sqn(loc, sqn,l)
    #
    time_ = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    message = {"nodeID":"clien_1","send_time": time_,"oper": "key-value", "message":{"oper-type": "write", "bucket_name":"db","content":{"class":"8:00","type":"MS"}, "sqn_no":sqn_}}
    send_message(message, sqn_, time_,"client1")
    sqn_ = get_sqn(loc, sqn,l)
    time_ = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    message = {"nodeID":"clien_1","send_time": time_,"oper": "key-value", "message":{"oper-type": "write", "bucket_name":"db","content":{"class":"9:00","type":"MS"}, "sqn_no":sqn_}}
    send_message(message, sqn_, time_,"client1")
    time_ = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    sqn_ = get_sqn(loc, sqn,l)    
    message = {"nodeID":"clien_1","send_time": time_,"oper": "key-value", "message":{"oper-type": "write", "bucket_name":"db","content":{"class":"10:00","type":"MS"}, "sqn_no":sqn_}}
    send_message(message, sqn_, time_,"client1")
    #slp = random.uniform(0.1, 0.3)
    #time.sleep(slp)
        
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
            
def client_2(sqn, loc,l):
    print("Starting client 2")
    sqn_ = get_sqn(loc, sqn,l)
    time_ = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    message = {"nodeID":"clien_2","send_time": time_,"oper": "key-value", "message":{"oper-type": "searchbynodeID", "bucket_name":"db","content":[1], "sqn_no":sqn_}}
    send_message(message, sqn_, time_,"client2")
    sqn_ = get_sqn(loc, sqn,l)
    time_ = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    message = {"nodeID":"clien_2","send_time": time_,"oper": "key-value", "message":{"oper-type": "deletebynodeID", "bucket_name":"db","content":[1], "sqn_no":sqn_}}
    send_message(message, sqn_, time_,"client2")
    time_ = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    sqn_ = get_sqn(loc, sqn,l)    
    message = {"nodeID":"clien_2","send_time": time_,"oper": "key-value", "message":{"oper-type": "searchbynodeID", "bucket_name":"db","content":[1], "sqn_no":sqn_}}
    send_message(message, sqn_, time_,"client2")
    #slp = random.uniform(0.1, 0.3)
    #time.sleep(slp)
        

if __name__ == '__main__':
    manager = Manager()
    sqn = manager.Value('i',0)
    loc = manager.Value('i',0)
    l = manager.Lock()
    cl1 = multiprocessing.Process(target=client_1, args = (sqn, loc,l))
    cl2 = multiprocessing.Process(target=client_2, args = (sqn, loc,l))
    resp = multiprocessing.Process(target=response)
    cl1.start()
    cl2.start()
    resp.start()
    cl1.join()
    cl2.join()
    resp.join()


    
