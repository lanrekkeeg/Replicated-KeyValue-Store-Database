import socket
import multiprocessing
import sys
from global_conf import *
import logging
from util import *
import json
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('test')
groupview = {1:'127.0.0.1:9001',2:'127.0.0.1:9002',3:'127.0.0.1:9004',4:'127.0.0.1:9005',5:'127.0.0.1:9006',6:'127.0.0.1:9007'}

import socket
import time


class BroadcastSender:
    def __init__(self, id,ip='127.0.0.1', port=37020):
  
        logger.debug("Broadcaster object is intiated...")
        self.id = id
        self.ip = ip
        self.port = port
        self.broad_cast_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.broad_cast_sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        # Enable broadcasting mode
        self.broad_cast_sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
  
    def broadcast_message(self, message):
        """
        convert into byte format
        """
        message = json.dump(message)
        message = str.encode(message)
        self.broad_cast_sender.settimeout(0.2)
        logger.debug("Broadcasting message ...")
        self.broad_cast_sender.sendto(message, (self.ip, self.port))
        logger.debug("Message broadcasted ...")

        
    
class Broadcaster(multiprocessing.Process):
    def __init__(self, id, lis=0,broad=0):
        super(Broadcaster, self).__init__()

        self.listener = lis
        self.broadcast = broad
        logger.debug("Broadcaster object is intiated...")
        self.id = id
        self.broad_cast_receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
        self.broad_cast_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.broad_cast_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.broad_cast_sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        # Enable broadcasting mode
        self.broad_cast_sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.broad_cast_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.broad_cast_receiver.bind(("", 37020))
        
    
    def run(self):
    
        if self.listener:    
            self.listen_to_broadcast_message()
        elif self.broadcast:
            self.broad_cast_message()
            
    def listen_to_broadcast_message(self):
        logger.debug("Broadcaster listerner module is intiated...")

        while True:
            # Thanks @seym45 for a fix
            data, addr = self.broad_cast_receiver.recvfrom(1024)
            # perform operation base on this data
            
            # check for winner of election
            # data = data.decode()
            # data = json.load(data)
            # if data['oper'] == 'election':
                # is election started?
                  # isElection = True
                # is election completed?
                  # leaderID = data['message']['leaderID']
                  # start ping module
                # who 
            print("received message: %s"%data)
        
    
    # we will pass message we want to broadcast
    def broad_cast_message(self):
        self.broad_cast_sender.settimeout(0.2)
        message = b"message from Prcoess"
        logger.debug("Broadcast sender module is intiated..")
        while True:
            logger.debug("Sending message")
            self.broad_cast_sender.sendto(message, ('192.168.0.255', 37020))
            print("message sent!")
            time.sleep(1)
            
            
class Election:

    def __init__(self, id):
        self.leader = False
        self.Election = False
        self.id = int(id)
        self.groupview = groupview
        self.sub_group = dict()  # all IDS less than self.id will be stored in this dict
        self.broadcaster = BroadcastSender(self.id)
        self.higer_node_sockets = []
        self.participation = True

            
    def create_connections_to_other_hosts(self):
        """
        Create connection for host acknowledge as part of the algoithm
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for key, val in self.sub_group.items():
            ip, port = val.split(':')
            s.connect((ip, int(port)))
            s.settimeout(1)
            self.higer_node_sockets.append(s)
    
    def close_connection(self):
        """
        Closing socket connection 
        """
        for sock in self.higer_node_sockets:
            sock.close()
            
        
    def check_acknowledgement(self):
        """
        check acknowledgement on different sockets 
        """
        ack = 0
        time_out_soc = 0
        for sock in self.higer_node_sockets:
            try:
                data = sock.recv(1024)
                ack += 1 
                break  # as there is sonme node with higher id exist, so need to continue
            except socket.timeout as exp:
                time_out_soc += 1
                pass
        if ack >= 1:
            self.participation = False
        elif time_out_soc == len(self.higer_node_sockets):
            self.leader = True
        else:
            logger.error("Something is wrong with sockets..")
        
        
    def run(self):
        """
        """
        
        self.groupview = sort_dict(self.groupview)
        logger.debug("Node group view after sorting:{}".format(self.groupview))
        self.sub_group =  dict((k, v) for k, v in self.groupview.items() if k > self.id)
        logger.debug("Sub Node group view:{}".format(self.sub_group))
        
        if len(self.sub_group) == 0:
            time.sleep(2) # wait for other to finish the election
            message = {'id': self.id,'host': '127.0.0.1', 'port':'Null', 'channel': 'election', 'message':{'ElectionStatus':'complete', 'leader': self.id }}
            self.broadcaster(message)
            """
            You are at the top
            1. wait some time
            2. broadcast yourself as leader
            """
        else:
            self.create_connections_to_other_hosts()
            self.check_acknowledgement()
            if self.leader:
                logger.info("Election Process Complete, I am winner")
                message = {'id': self.id,'host': '127.0.0.1', 'port':'Null', 'channel': 'election', 'message':{'ElectionStatus':'complete', 'leader': self.id }}
                self.broadcaster(message)
                # broacast thread
                logger.info("Starting Health Broadcaster")
                broad_cast = multiprocessing.Process(target=broad_cast_health, args = (self.id, self.broadcaster))
                broad_cast.start()
                broad_cast.join()
                logger.info("Health Broadcaster started ...")
                logger.info("Terminating Election Process as it is of no use now, election is already finish.")
                self.close_connection()
                return
            else:
                # exiting election process
                logger.info("Higher node available, backing from election")
                self.close_connection()
                return
        
        
        
class CareTakerServer(multiprocessing.Process):
    def __init__(self, client_conn, client_addr):
        super(CareTakerServer, self).__init__()
        self.client_conn = client_conn
        self.client_addr = client_addr
        

    # Override run method
    def run(self):
        logger.debug("process is spawn for new client")
        # Message to be sent to client
        while True:
            # Receive message from client
            data = self.client_conn.recv(1024)
            if not data:
                break
            else:
                print("Recevied message from client, message is {}".format(data.decode()))
                self.client_conn.send(data)
                # unmarshal request 
                # perform operation
                # perform action
                # send back request
                pass
            #self.server_socket.sendto(str.encode(message), self.client_address)
            

class ClientHandler(multiprocessing.Process):

    def __init__(self, id, ip):
        super(ClientHandler, self).__init__()

        self.id = id
        self.port = groupview[id]
        self.ip = ip
        
    def run(self):
        logger.debug("Client Handlers is started ...")
        # Create a UDP socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
        # Server application IP address and port
        server_address = self.ip
        server_port = self.port
    
        # Buffer size
        buffer_size = 1024
    
        # Bind socket to address and port
        server_socket.bind((server_address, server_port))
        print('ClientHandler Server Up and Running.... {}:{}'.format(server_address, server_port))
        
        server_socket.listen()
        
        while True:
            # Receive message from client
            conn, addr = server_socket.accept()
            print ('New client connected, address:', addr)
            #data, address = server_socket.recvfrom(buffer_size)
            #print('Received message \'{}\' at {}:{}'.format(data.decode(), address[0], address[1]))
            # Create a server process
            p = CareTakerServer(conn,addr)
            p.start()
            p.join()
        
        
    
        
def ping(port):
    """
    Check for health
    1. store time called last time
    2. rece broadcast message after id/max_id + 1 sec
    3. if message rec then check last time
    4. else send election notification
    """
    broad_cast_receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
    broad_cast_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    broad_cast_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    broad_cast_sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    # Enable broadcasting mode
    broad_cast_sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    broad_cast_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    broad_cast_receiver.bind(("", port))
    #last_time = current time 
    while True:
        data, addr = broad_cast_receiver.recvfrom(1024)
        # parse it
        data = data.decode()
        data = json.loads(data)
        if data.get('ping') is not None:
            #current_ping =  current ping time
            pass
        
def broad_cast_health(id, broad_caster):
    """
    broadcast health if master
    1. start broadcasting health at interval of 1 second
    """
    
    pass
            
if __name__ == '__main__':
    # 1. start group view process
    # 2. start sockets (also needed for election Process and other operation) 
    # 3. start election process
    # 4. Incase of victory, start serving the request
    # 5. Incase of victory start broadcasting health
    # 6. Incase of failure start ping module to monitor leader health
    # 7. Future start file syncher 
    logger.debug("Starting Servers .....")

    id = sys.argv[1]
    clients = ClientHandler(int(id),'127.0.0.1')
    clients.start()
    broad = Broadcaster(1,lis=1)
    broad2 = Broadcaster(1,broad=1)
    broad.start()
    broad2.start()
    broad.join()
    broad2.join()
    clients.join()
    
    # wait for some time
    # send election message that election is started
    #process.append(multiprocessing.Process(target=broad.listen_to_broadcast_message, args=()))
    #process.append(multiprocessing.Process(target=broad2.broad_cast_message, args=()))

    #for proc in process:
        #proc.daemon = True

        #proc.start()
        #proc.join()
    
    
    
    