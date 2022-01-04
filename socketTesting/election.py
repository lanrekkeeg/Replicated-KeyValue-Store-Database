import socket
import multiprocessing
from multiprocessing import Manager

import sys
#import global_conf as glob_var
import logging
import json
import datetime

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('test')

#groupview = {1:'127.0.0.1:9001',2:'127.0.0.1:9002',3:'127.0.0.1:9004',4:'127.0.0.1:9005',5:'127.0.0.1:9006',6:'127.0.0.1:9007'}

import socket
import time


class BroadcastSender:
    def __init__(self, id, ip='192.168.0.255', port=37020):
  
        logger.debug("Node:{},Broadcaster object is intiated...".format(id))
     
        
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
        message = json.dumps(message)
        message = str.encode(message)
        #self.broad_cast_sender.settimeout(0.2)
        #logger.debug("Broadcasting message ...")
        self.broad_cast_sender.sendto(message, (self.ip, self.port))
        #logger.debug("Message broadcasted ...")

        
    
class Broadcaster(multiprocessing.Process):
    def __init__(self, id, groupView, leaderID, Leader, isElection, participation, lis=0,broad=0):
        super(Broadcaster, self).__init__()
        #self.glob_var = glob_
        
        self.groupView = groupView
        self.leaderID = leaderID
        self.Leader = Leader
        self.isElection = isElection
        self.participation = participation
        self.broadcaster = BroadcastSender(id)
        self.listener = lis
        self.broadcast = broad
        logger.debug("Node:{},Broadcaster object is intiated...".format(id))
        self.id = id
        self.broad_cast_receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
        self.broad_cast_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.broad_cast_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.broad_cast_sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        # Enable broadcasting mode
        self.broad_cast_sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.broad_cast_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.broad_cast_receiver.bind(("192.168.0.255", 37020))
        
        self.health_broadcast = None
        
    
    def run(self):
    
        if self.listener:    
            self.listen_to_broadcast_message()
        elif self.broadcast:
            self.broad_cast_message()
            
    def listen_to_broadcast_message(self):
        logger.debug("Node:{},Broadcaster listerner module is intiated...".format(id))
        while True:
            # Thanks @seym45 for a fix
            data, addr = self.broad_cast_receiver.recvfrom(1024)
            # perform operation base on this data
            
            # check for winner of election
            data = data.decode()
            try:
                data = json.loads(data)
                logger.debug("Node:{}, Broadcast received:{}".format(self.id, data))
            except Exception as exp:
                logger.error("Node:{}, fail to parse broadcasted message,error is {}".format(self.id,str(exp)))
                continue
            # reject self send messages
            
            if data.get("oper",None) == "status":
                logger.info("{},{}:*********************************************************************************************************************".format(self.Leader.value,self.leaderID.value))
            # itself id will be updated, won't cause issue if leader itself update itself
            if data.get("oper",None) == "response":
                logger.info("Node:{}, reponse is recieved for status, updating leaderID:{}".format(self.id,data['message']['leader']))
                message = data['message']
                self.leaderID.value = int(message['leader'])
                
            #elif data.get('nodeID',None) != self.id: 
            elif True:
                if data.get('oper', None) == 'status':
                    message = data['message']
                    if message.get('status',None) == 'leader':
                        logger.info("{},*********************************************************************************************************************".format(self.Leader.value))

                        if self.Leader.value:
                            logger.info("Node:{},returning status request fro leader...")
                            message = {'nodeID':self.id,'oper': 'response','message':{'leader':self.leaderID.value}}
                            message = json.dumps(message)
                            message = message.encode()
                            self.broad_cast_sender.sendto(message, ('192.168.0.255', 37020))
    
                    
                if data.get('oper', None) == 'election':
                    message = data['message']
                    # is election started?
                    
                    if message['ElectionStatus'] == 'started':
                        logger.info("&&&&&&&&&&&&&&&& Election message received, stopping and resetting all settings &&&&&&&&&&&&&&")
                        self.leaderID.value = -1
                        self.Leader.value = 0
                        self.isElection.value = 1 # may be need to remove incase
                        try:
                            self.health_broadcast.terminate()
                        except Exception as exp:
                            logger.info("Node:{}, issue with closing broadcast module, error is {}".format(self.id, exp))
                        
                    if message['ElectionStatus'] == 'complete' and int(data.get('nodeID',None)) != int(self.id):
                        logger.info("Node:{}, receive election complete message, starting ping module. Message is :{}".format(self.id, message))
                        self.isElection.value = 0
                        self.leaderID.value = int(data['message']['leader'])
                        self.health_broadcast = multiprocessing.Process(target=recv_ping, args = (self.id,37020, self.broadcaster, self.groupView,self.leaderID,self.Leader,self.participation, self.isElection))
                        self.health_broadcast.start()
                        #broad_cast.join()
                    
                if data.get('oper',None) == 'groupview' and data.get('nodeID',None) != self.id:
                    logger.info('Node:{}, Groupview data is, {}'.format(self.id, data))
                    temp_dict = self.groupView['groupView']
                    temp_dict.update({data['nodeID']: data['message']['host'] + ':' + str((data['message']['port']))})
                    self.groupView['groupView'] = temp_dict
                    logger.debug("@@@@@@@@ Node:{}, updated group view is,{}    @@@@@@@@@".format(self.id, self.groupView['groupView']))
                    
                    # is election completed?
                      # leaderID = data['message']['leaderID']
                      # start ping module
                # who 
            print("received message: %s"%data)
        
    
    # we will pass message we want to broadcast
    def broad_cast_message(self):
        self.broad_cast_sender.settimeout(0.2)
        message = {'message':'test'}
        message = json.dumps(message)
        message = message.encode()
        logger.debug("Node:{},Broadcast sender module is intiated..".format(id))
        while True:
            logger.debug("Node:{},Sending message".format(id))
            self.broad_cast_sender.sendto(message, ('192.168.0.255', 37020))
            print("message sent!")
            time.sleep(1)
            
            
class Election(multiprocessing.Process):

    def __init__(self, id,groupView,leaderID,Leader,isElection, participation, client_sockt=None):
        super(Election, self).__init__()
        self.groupView = groupView
        self.leaderID = leaderID
        self.Leader = Leader
        self.isElection = isElection
        self.participation = participation
        self.leader = False
        self.election = False
        self.id = id
        self.sub_group = dict()  # all IDS less than self.id will be stored in this dict
        self.broadcaster = BroadcastSender(self.id)
        self.higer_node_sockets = []
        self.client_sockt = client_sockt

            
    def create_connections_to_other_hosts(self):
        """
        Create connection for host acknowledge as part of the algoithm
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        for key, val in self.sub_group.items():
            ip, port = val.split(':')
            try:
                s.connect((ip, int(port)))
                s.settimeout(1)
                self.higer_node_sockets.append(s)
            except Exception as exp:
                logger.error("Node:{}, Got error while creating socket for election client".format(self.id))
    
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
            self.participation.value = 0
        elif time_out_soc == len(self.higer_node_sockets):
            self.leader = True
        else:
            logger.error("Node:{},Something is wrong with sockets..".format(id))
    
    def result_routine(self):
        """
        announce result, start the health broadcaster
        """
        
        logger.info("Node:{},Starting result routine...".format(self.id))
        logger.info("Node:{},Election Process Complete, I am winner".format(id))
        message = {'nodeID': self.id, 'oper': 'election', 'message':{'ElectionStatus':'complete', 'leader': self.id }}
        self.broadcaster.broadcast_message(message)
        self.leaderID.value = self.id
        self.Leader.value = 1
        logger.debug("updating global var...{},{}".format(self.leaderID.value, self.Leader.value))
        # broacast thread
        logger.info("Node:{},Starting Health Broadcaster".format(id))
        broad_cast = multiprocessing.Process(target=broad_cast_health, args = (self.id, self.Leader, self.broadcaster))
        broad_cast.start()
        #broad_cast.join()
        logger.info("Node:{},Health Broadcaster started ...".format(id))
        logger.info("Node:{},Terminating Election Process as it is of no use now, election is already finish.".format(id))
        self.close_connection()
        logger.info("Node:{},result routine finish....".format(self.id))
        self.participation.value = 0
        self.isElection.value = 0

        
    def run(self):
        """
        """
        self.participation.value = 1
        # new addition
        self.isElection.value = 1
        logger.info("################################ Election is started ##########################################")
        sorted_groupview = sort_dict(self.groupView['groupView'])
        logger.debug("Node:{},Node group view after sorting:{}".format(id, sorted_groupview))
        self.sub_group =  dict((k, v) for k, v in sorted_groupview.items() if k > self.id)
        logger.debug("Node:{},Sub Node group view:{}".format(id, self.sub_group))
                
        if len(self.sub_group) == 0:
            """
            You are at the top
            1. wait some time
            2. broadcast yourself as leader
            """
            time.sleep(2) # wait for other to finish the election
            self.result_routine()
            
        else:
            # here we check if check if this node any receive any socket from any other client if not then it means it is first of it's kind
            if self.client_sockt is not None:
                message = {'nodeID': self.id, 'oper': 'election', 'message':{'ElectionStatus':'running','ack': True}}
                message = json.dumps(message)
                message = str.encode(message)
                self.client_sockt.send(message)
                
            self.create_connections_to_other_hosts()
            self.check_acknowledgement()
            if self.leader:
                    # announce the result
                    self.result_routine()
                    return
            else:
                # exiting election process
                logger.info("Node:{},Higher node available, backing from election".format(id))
                self.close_connection()
                return
        
        
        
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
                        message = {'nodID': self.id, 'port':port, 'oper': 'election', 'message':{'ElectionStatus':'running','ack': True}}
                        message = json.dumps(message)
                        message = str.encode(message)
                        self.client_sockt.send(message)
                        if not self.participation.value:
                            elec = Election(self.id, self.groupView, self.leaderID, self.Leader,self.isElection,self.participation,self.client_conn)
                            elec.start()
                        
class GroupView(multiprocessing.Process):
    def __init__(self, id ,port, groupView, leaderID, Leader):
        super(GroupView, self).__init__()
        self.groupView = groupView
        self.leaderID = leaderID
        self.Leader = Leader
        self.id = id
        self.broadcaster = BroadcastSender(self.id)
        self.port = port

        
        
    # Override run method
    def run(self):
        logger.debug("Node:{}, Group view process started, broadcasting port and ip".format(id))
        # Message to be sent to client
        while True:
            host = socket.gethostbyname(socket.gethostname())
            message = {'oper': 'groupview','nodeID':self.id, 'message':{'host':host,'port':self.port}}
            self.broadcaster.broadcast_message(message)
            time.sleep(0.3)

            
            

class ClientHandler(multiprocessing.Process):

    def __init__(self, id, ip, port, groupView, leaderID, Leader, isElection, participation):
        super(ClientHandler, self).__init__()
    
        self.groupView = groupView
        self.leaderID = leaderID
        self.Leader = Leader
        self.isElection = isElection
        self.participation = participation
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
            p = CareTakerServer(self.id, conn,addr, self.groupView, self.leaderID, self.Leader, self.isElection, self.participation)
            p.start()
            p.join()
        
class Startup_Routine(object):
    def __init__(self,id,groupView, leaderID, Leader, isElection, participation):
        '''
            1. check for the leader
            2. if there is leader, then check if it is legal leader
            3. if not legal leader then start the election
            
            if not self.find_leader():
                start the election process
            else if self.find_leader():
                check node id, if smaller then bully and start the election
        '''
        self.groupView = groupView
        self.leaderID = leaderID
        self.Leader = Leader
        self.isElection = isElection
        self.participation = participation
        
        self.id =  id
        logger.debug("Node:{}, startup routine started....".format(self.id))
        self.broadcaster = BroadcastSender(self.id)
        logger.info("Node:{}, sending message to find the leader".format(self.id))
        if self.isElection.value:
            logger.info("Node:{},*********Election is in progress********")
            time.sleep(10)
        self.find_leader()
        time.sleep(5)
        if self.leaderID.value == -1: # -1 mean none
            logger.info("Node:{}, No leader node found, starting fresh election")
                # start the election
                
            # new addition ....
            message = {'nodeID': self.id, 'oper': 'election', 'message':{'ElectionStatus':'started'}}
            self.broadcaster.broadcast_message(message)
            
            election = Election(self.id, self.groupView, self.leaderID, self.Leader, self.isElection,self.participation,None)
            election.start()
            #election.join()
            logger.info("Startup routine finish with election")
            
        elif self.leaderID.value < int(self.id):
                # bully old node
            logger.info("Node:{}, leader found but not valid, bulllying leader:{} and starting election...".format(self.id, self.leaderID.value))
            message = {'nodeID': self.id, 'oper': 'election', 'message':{'ElectionStatus':'started'}}
            self.broadcaster.broadcast_message(message)
            time.sleep(0.2)
            election = Election(self.id, self.groupView, self.leaderID, self.Leader, self.isElection, self.participation,None )
            election.start()
            #election.join()
                # start the election
        elif self.leaderID.value != -1: # mean not None
            logger.debug("Node:{}, leader already exist, starting ping module for this node...")
            self.isElection.value = 0
            
            broad_cast = multiprocessing.Process(target=recv_ping, args = (self.id,37020, self.broadcaster, self.groupView,self.leaderID,self.Leader,self.participation,self.isElection))
            broad_cast.start()
            #broad_cast.join()
            
            
        
    def find_leader(self):
        """
        1. broadcast message 
        2. wait for leader message (timeout 0.2 second)
        """
        logger.debug("Node:{}, sending broadcast message to find the leader".format(self.id))
        message = {"oper":"status", "message":{"status":"leader"}}
        self.broadcaster.broadcast_message(message)
            
        
    
        
def recv_ping(id,port, broad_caster, groupView, leaderID, Leader, participation,isElection):
    
    """
    Check for health
    1. store time called last time
    2. rece broadcast message after id/max_id + 1 sec
    3. if message rec then check last time
    4. else send election notification
    """
    logger.info("XXXXXXXXXXXXXXXXX Starting Ping Service XXXXXXXXXXXXXXXX")

    broad_cast_receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
    broad_cast_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    #broad_cast_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    #broad_cast_sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    # Enable broadcasting mode
    #broad_cast_sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    broad_cast_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    broad_cast_receiver.bind(("", port))
    last_time = datetime.datetime.now() 
    while not isElection.value:
        data, addr = broad_cast_receiver.recvfrom(1024)
        # parse it
        curr_time = datetime.datetime.now() 

        data = data.decode()
        data = json.loads(data)
        
        if data.get('ping') is not None:
            last_time = curr_time
            #current_ping =  current ping time
            # check time diff
            # if voilates
            # wait for t second
            # check election
        diff =  curr_time - last_time
        #logger.info("Node:{}, time diff for ping message is {} and message is {}".format(id, diff, data))
        logger.info("Ping message is {}".format(data))

        diff = diff.total_seconds()
        if diff > 2: # to call off for election
        
            # check if election is already started?
            # broadcast message for election
            # if not then start the election
            logger.info("$$$$$$$$$$$$$$ Leader Found Dead $$$$$$$$$$$$")
            message = {"nodeID":id,'host': '127.0.0.1', 'oper': 'election', 'message':{'ElectionStatus':'started' }}
            broad_caster.broadcast_message(message)
            #message = json.dumps(message)
            #message = str.encode(message)
            #broad_caster.send(message)
            # sedning again
            broad_caster.broadcast_message(message)
            election = Election(id, groupView, leaderID, Leader, isElection, participation,None)

            election.start()
            #election.join()
            return
    
    logger.info("^^^^^^^^^ Stopping Ping Service ^^^^^^^^^^^^^")
    
            

         
        
            
def sort_dict(node_group):
    """
    return sorted dictionary by key
    """
    
    sorted_node_id = dict(sorted(node_group.items(), key = lambda x:x[0]))
    return sorted_node_id
    
        
        
def broad_cast_health(id,Leader, broad_caster):
    
    """
    broadcast health if master
    1. start broadcasting health at interval of 1 second
    """
    logger.info("%%%%%%%%%%%%%%% starting broadcast health %%%%%%%%%%%%%%%%%%%%%")
    check = 1
    while check:
        message = {"id": id, "ping": True}
        #message = json.dumps(message)
        #message = str.encode(message)
        broad_caster.broadcast_message(message)
        time.sleep(0.1)
        check = Leader.value  # stop when there is no leader
    logger.info("Node:{},**********STOPPING HEALTH CHECK*************".format(id))    
    return
if __name__ == '__main__':
    # 1. start group view process
    # 2. start sockets (also needed for election Process and other operation) 
    # 3. start election process
    # 4. Incase of victory, start serving the request
    # 5. Incase of victory start broadcasting health
    # 6. Incase of failure start ping module to monitor leader health
    # 7. Future start file syncher 
    logger.debug("Starting Servers .....")
    manager = Manager()

    groupView = manager.dict({'groupView':{}})
    leaderID =  manager.Value('i', -1)
    Leader = manager.Value('i', 0) # either 0 or 1
    isElection = manager.Value('i', 0) # either 0 or 1
    participation = manager.Value('i', 0) # either 0 or 1

    
    #global id
    #global port
    id = sys.argv[1]
    port = int(sys.argv[2])
    
    broad = Broadcaster(id, groupView, leaderID, Leader,isElection ,participation, lis=1)
    broad2 = Broadcaster(id, groupView, leaderID, Leader,isElection, participation, lis=0)
    clients = ClientHandler(id,socket.gethostbyname(socket.gethostname()), port, groupView, leaderID, Leader, isElection, participation)
    view = GroupView(id,port,groupView, leaderID, Leader)
    broad.start()
    broad2.start()
    clients.start()
    view.start()
    
    routine = Startup_Routine(id,groupView, leaderID, Leader, isElection, participation)
    time.sleep(1) # to give  time to form group view
    
    # check for leader
    
    #if isElection:
    #    elc = Election(id)
    #    elc.start()
    
    '''
    

    '''
   
    
    broad.join()
    broad2.join()
    view.join()
    clients.join()


    #elc.join()

    
    
    # wait for some time
    # send election message that election is started
    #process.append(multiprocessing.Process(target=broad.listen_to_broadcast_message, args=()))
    #process.append(multiprocessing.Process(target=broad2.broad_cast_message, args=()))

    #for proc in process:
        #proc.daemon = True

        #proc.start()
        #proc.join()
    
    
    
    