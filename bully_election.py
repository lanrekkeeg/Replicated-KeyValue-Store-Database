import socket
import multiprocessing
from multiprocessing import Manager
from replica_handler import ReplicaHandler
import sys
#import global_conf as glob_var
import logging
from util import *
import json
import datetime
from broadcast import Broadcaster, BroadcastSender
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('test')

#groupview = {1:'127.0.0.1:9001',2:'127.0.0.1:9002',3:'127.0.0.1:9004',4:'127.0.0.1:9005',5:'127.0.0.1:9006',6:'127.0.0.1:9007'}

import socket
import time

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

        
    def run(self):
        """
        """
        self.participation.value = 1
        logger.info("Election is started ......")
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
        
        