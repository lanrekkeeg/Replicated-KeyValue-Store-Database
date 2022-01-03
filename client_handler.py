
import socket
import multiprocessing
import sys
#import global_conf as glob_var
import logging
from util import *
import json
import datetime

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('test')

#groupview = {1:'127.0.0.1:9001',2:'127.0.0.1:9002',3:'127.0.0.1:9004',4:'127.0.0.1:9005',5:'127.0.0.1:9006',6:'127.0.0.1:9007'}

import socket
import time

class CareTakerServer(multiprocessing.Process):
    def __init__(self, id, client_conn, client_addr, groupView, leaderID, Leader, isElection, participation):
        super(CareTakerServer, self).__init__()
        self.groupView = groupView
        self.leaderID = leaderID
        self.Leader = Leader
        self.isElection = isElection
        self.participation = participation
        self.client_conn = client_conn
        self.client_addr = client_addr
        self.id = id
        
    # Override run method
    def run(self):
        logger.debug("Node:{},process is spawn for new client".format(id))
        # Message to be sent to client
        while True:
            # Receive message from client
            data = self.client_conn.recv(1024)
            if not data:
                break
            else:
                data = data.decode()
                data = json.loads(data)
                print("Node:{},Recevied message from client, message is {}".format(self.id, data.decode()))
                if data.get('oper') == 'election':
                    msg = data['message']
                    if msg['ElectionStatus'] == 'running':
                        logger.info("Node:{}, receive messagem from election".format(self.id))
                        # start election, by passing the client socket if available
                        message = {'id': self.id, 'port':port, 'oper': 'election', 'message':{'ElectionStatus':'running','ack': True}}
                        message = json.dumps(message)
                        message = str.encode(message)
                        self.client_sockt.send(message)
                        if not self.participation.value:
                            elec = Election(self.id, self.groupView, self.leaderID, self.Leader,self.isElection,self.participation,self.client_conn)
                            elec.start()
                        
                        
class ClientHandler(multiprocessing.Process):

    def __init__(self, id, ip, port, groupView, leaderID, Leader, isElection, participation):
        super(ClientHandler, self).__init__()
    
        self.groupView = groupView
        self.leaderID = leaderID
        self.Leader = Leader
        self.isElection = isElection
        self.id = id
        self.port = port
        self.ip = ip
        
    def run(self):
        logger.debug("Node:{},Client Handlers is started ...".format(id))
        # Create a UDP socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        # Server application IP address and port
        server_address = self.ip
        server_port = self.port
    
        # Buffer size
        buffer_size = 1024
    
        # Bind socket to address and port
        server_socket.bind((server_address, server_port))
        logger.debug('Node:{},ClientHandler Server Up and Running.... {}:{}'.format(id,server_address, server_port))
        
        server_socket.listen()
        
        while True:
            # Receive message from client
            conn, addr = server_socket.accept()
            print ('New client connected, address:', addr)
            #data, address = server_socket.recvfrom(buffer_size)
            #print('Received message \'{}\' at {}:{}'.format(data.decode(), address[0], address[1]))
            # Create a server process
            p = CareTakerServer(self.id, conn,addr, self.groupView, self.leaderID, self.Leader, self.isElection)
            p.start()
            p.join()