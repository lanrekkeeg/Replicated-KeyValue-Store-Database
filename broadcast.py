import socket
import time
import multiprocessing
from multiprocessing import Manager
import sys
#import global_conf as glob_var
import logging
from util import *
import json
import datetime
from fault_tolerant import recv_ping
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('test')
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
    def __init__(self, id, groupView, leaderID, Leader, isElection, participation, port, lock, sqn):
        super(Broadcaster, self).__init__()
        #self.glob_var = glob_
        self.sqn = sqn
        self.lock = lock
        self.host = socket.gethostbyname(socket.gethostname())
        self.port = port
        self.groupView = groupView
        self.leaderID = leaderID
        self.Leader = Leader
        self.isElection = isElection
        self.participation = participation
        self.broadcaster = BroadcastSender(id)
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
    
        self.listen_to_broadcast_message()
            
    def listen_to_broadcast_message(self):
        logger.debug("Node:{},Broadcaster listerner module is intiated...".format(id))
        
        
        while True:
            # Thanks @seym45 for a fix
            try:
                data, addr = self.broad_cast_receiver.recvfrom(1024)
                # perform operation base on this data
                
                # check for winner of election
                data = data.decode()
                try:
                    data = json.loads(data)
                    #logger.debug("Node:{}, Broadcast received:{}".format(self.id, data))
                except Exception as exp:
                    logger.error("Node:{}, fail to parse broadcasted message,error is {}".format(self.id,str(exp)))
                    continue
                # reject self send messages
                
                # itself id will be updated, won't cause issue if leader itself update itself
                if data.get("oper",None) == "response":
                    #logger.info("Node:{}, reponse is recieved for status, updating leaderID:{}".format(self.id,data['message']['leader']))
                    message = data['message']
                    self.leaderID.value = int(message['leader'])
                    
                #elif data.get('nodeID',None) != self.id: 
                elif True:
                    if data.get('oper', None) == 'status':
                        message = data['message']
                        if message.get('status',None) == 'leader':
                            #logger.info("{},*********************************************************************************************************************".format(self.Leader.value))
                            self.lock.acquire()
                            val = self.Leader.value
                            self.lock.release()
                            if val == 1:
                                #file = open("test.txt",'a+')
                                #file.write(str(self.leaderID.value)+'/n')
                                #file.close()
                                logger.info("#####Returning status request:{} from leader######".format(message))
                                logger.info("###### host:{},  ###### port:{}, LeaderID:{}".format(self.host, self.port, self.leaderID.value))
                                message = {'nodeID':self.id,'oper': 'response','message':{'leader':self.leaderID.value,"host":self.host, "port":self.port}}
                                message = json.dumps(message)
                                message = message.encode()
                                self.broad_cast_sender.sendto(message, ('192.168.0.255', 37020))
        
                        
                    if data.get('oper', None) == 'election':
                        message = data['message']
                        # is election started?
                        
                        if message['ElectionStatus'] == 'started':
                            logger.info("&&&&&&&&&&&&&&&& Election message received, stopping and resetting all settings &&&&&&&&&&&&&&")
                            self.lock.acquire()
                            self.leaderID.value = -1
                            self.Leader.value = 0
                            self.sqn.value = -1
                            self.isElection.value = 1 # may be need to remove incase
                            self.lock.release()
                            #try:
                            #    self.health_broadcast.terminate()
                            #except Exception as exp:
                            #    logger.info("Node:{}, issue with closing broadcast module, error is {}".format(self.id, exp))
                            
                        if message['ElectionStatus'] == 'complete' and int(data.get('nodeID',None)) != int(self.id):
                            logger.info("Node:{}, receive election complete message, starting ping module. Message is :{}".format(self.id, message))
                            self.lock.acquire()
                            self.isElection.value = 0
                            self.leaderID.value = int(data['message']['leader'])
                            self.Leader.value = 0 # i am not leader
                            self.lock.release()
                            self.health_broadcast = multiprocessing.Process(target=recv_ping, args = (self.id,37020, self.broadcaster, self.groupView,self.leaderID,self.Leader,self.participation, self.isElection, self.lock))
                            self.health_broadcast.start()
                            #broad_cast.join()
                        
                    if data.get('oper',None) == 'groupview' and data.get('nodeID',None) != self.id:
                        #logger.info('Node:{}, Groupview data is, {}'.format(self.id, data))
                        temp_dict = self.groupView['groupView']
                        temp_dict.update({data['nodeID']: data['message']['host'] + ':' + str((data['message']['port']))})
                        self.groupView['groupView'] = temp_dict
                    #logger.debug("@@@@@@@@ Node:{}, updated group view is,{}    @@@@@@@@@".format(self.id, self.groupView['groupView']))
            except  KeyboardInterrupt:
                logger.info("Keyboard is interrrupted...")
                #self.lock.acquire()
                #import sys
                #import os
                #os.system('sudo kill -9 {0}'.format(os.getpid()))

                #self.Leader.value = 0 # small hack
                self.broad_cast_sender.shutdown(1)
                self.broad_cast_sender.close()
                self.broad_cast_receiver.shutdown(1)
                self.broad_cast_receiver.close()
                
                    # is election completed?
                      # leaderID = data['message']['leaderID']
                      # start ping module
                # who 
            #print("received message: %s"%data)
        
    
  
            
            
                
        
