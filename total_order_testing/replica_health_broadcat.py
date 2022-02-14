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
    
def health(id):
    """
    """
    print("Starting response ")
    while True:
        '''
        temp_dict.update({data['nodeID']: {"host":data['message']['host'], "status":data['message']['status'],"lastcheck":time_}})

        '''
        message = {"nodeID":str(id),"oper": "groupView", "message":{"host": "abc", "status":"serving"}}
        send_message(message)
            

    
    #slp = random.uniform(0.1, 0.3)
    #time.sleep(slp)
        

if __name__ == '__main__':
    import uuid
    id = uuid.uuid4()
    manager = Manager()
    sqn = manager.Value('i',0)
    loc = manager.Value('i',0)
    l = manager.Lock()
    hlt = multiprocessing.Process(target=health,args=(id,))
    hlt.start()
    hlt.join()


    
