#!/usr/bin/env python

from logging import Logger
import socket
import struct
import json
import time
import multiprocessing
from multiprocessing import Manager

from broad_multi_cast import MulticastSend,MulticastRec





def get_recever():
    """
    """
    broad_cast_receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
    broad_cast_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    broad_cast_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    broad_cast_receiver.bind(("192.168.0.255", 37020))
    return broad_cast_receiver

def get_broadcaster():
    """
    """
    broad_cast_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    broad_cast_sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    broad_cast_sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    return broad_cast_sender
    
def send_message(message, broad_cast_sender):
    message = json.dumps(message)
    message = str.encode(message)    
    broad_cast_sender.sendto(message,("192.168.0.255", 37020))

def test_connection(ip, port):
    """
    testing connection
    """
    try:
        client  = get_sock()
        client.connect((ip, port))
        message = {"acquire":"master"}
        message = json.dumps(message)
        message = str.encode(message)
        client.send(message)
        
        data = client.recv(1024)
        data = data.decode()
        data = json.loads(data)
        if data.get("isLeader",None) == 1:
            client.close()
            print("Test passed")
            return 1
        else:
            client.close()
            print("Test failed")
            return 0
    except socket.error as exp:
        print("Error in testing connection, {}".format(exp))
        client.close()
        return 0
    return 1
    
def send_ping(broad_cast_sender):
    """
    """
    message = {"nodeID":"clien_2","oper": "status", "message":{"status": "leader","from":"client"}}
    send_message(message,broad_cast_sender)
    
def get_leader_ip():
    """
    """
    print("Checking for leader IP")
    time.sleep(3)
    broad = get_broadcaster()
    send_ping(broad)
    broad_cast_receiver = get_recever()
    while True:
        try:
            data, addr = broad_cast_receiver.recvfrom(1024)
        
        except Exception as exp:
            print("Error in receving multicat")
            exit(1)
        message = data.decode()
        message = json.loads(message)
        if message.get("oper",None) == "response":
            print(message)

            if message['message'].get('leader', None) is not None:
                print("Leader data is {}".format(message['message']))
                if test_connection(message['message']['host'], int(message['message']['port'])):
                    print("Returning leader ip to client")
                    return message['message']['host'],message['message']['port']
                    
        broad.close()
        broad_cast_receiver.close()
        broad_cast_receiver = get_recever()
        broad = get_broadcaster()
        send_ping(broad)
               
     
def get_stable_connection():
    """
    """
    pass
    
def get_sock():
    """
    """
    client  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client.settimeout(1)
    return client

def client_2(sqn, loc,l):
    print("Starting basic client...")
    
    client  = get_sock()
    ip, port = get_leader_ip()
    client.connect((ip, port))
    print("First connection is made...")
    while True:
        message = {"nodeID":"clien_2","oper": "key-value", "message":{"oper-type": "hello world"}}
        message = json.dumps(message)
        message = message.encode()
        try:
            client.send(message)
        except socket.error as exp:
            client.close()
            print("Exception while sending message error,{}".format(exp))
            print("Got error while receiving data, error is {}".format(exp))
            client  = get_sock()
            ip, port = get_leader_ip()
            client.connect((ip, port))
            continue
        
        try:
            data = client.recv(1024)
            print("message from server:{}".format(data.decode()))
        #except socket.timeout as exp:
        #    print("Timeout for socket")
        #    print("Got error while receiving data, error is {}".format(exp))
        #    client  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #    ip, port = get_leader_ip()
        #    client.connect((ip, port))
        except socket.error as exp:
            print("Got error while receiving data, error is {}".format(exp))
            client  = get_sock()

            ip, port = get_leader_ip()
            client.connect((ip, port))
            
    
    #slp = random.uniform(0.1, 0.3)
    #time.sleep(slp)
        

if __name__ == '__main__':
    manager = Manager()
    sqn = manager.Value('i',0)
    loc = manager.Value('i',0)
    l = manager.Lock()
    cl2 = multiprocessing.Process(target=client_2, args = (sqn, loc,l))
    cl2.start()
    cl2.join()


    
