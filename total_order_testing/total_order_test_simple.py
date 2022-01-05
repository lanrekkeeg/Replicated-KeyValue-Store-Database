#!/usr/bin/env python

import socket
import struct
import json
import time
import datetime
def main():
    MCAST_GRP = '224.1.1.1'
    MCAST_PORT = 5007
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
    sqn = 0
    while True:
        time_ = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        message = {"nodeID":"clien_1","send_time":time_,"oper": "key-value", "message":{"sqn_no":sqn,"oper-type": "write", "bucket_name":"db","content":{"class":"8:00","type":"MS"}}}
        message = json.dumps(message)
        message = str.encode(message)    
        sock.sendto(message, (MCAST_GRP, MCAST_PORT))
        sqn +=1
        print("message is sent ...")
        time.sleep(0.2)
        
        

if __name__ == '__main__':
    main()
