
import multiprocessing

#import global_conf as glob_var
import logging
from util import *

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('test')

import time
from broadcast import BroadcastSender
from bully_election import Election
from fault_tolerant import recv_ping

class Startup_Routine(object):
    def __init__(self,id,groupView, leaderID, Leader, isElection, participation, lock):
        '''
            1. check for the leader
            2. if there is leader, then check if it is legal leader
            3. if not legal leader then start the election
            
            if not self.find_leader():
                start the election process
            else if self.find_leader():
                check node id, if smaller then bully and start the election
        '''
        self.lock = lock
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
            
            election = Election(self.id, self.groupView, self.leaderID, self.Leader, self.isElection,self.participation,self.lock, None)
            election.start()
            #election.join()
            logger.info("Startup routine finish with election")
            
        elif self.leaderID.value < int(self.id):
                # bully old node
            logger.info("Node:{}, leader found but not valid, bulllying leader:{} and starting election...".format(self.id, self.leaderID.value))
            message = {'nodeID': self.id, 'oper': 'election', 'message':{'ElectionStatus':'started'}}
            self.broadcaster.broadcast_message(message)
            time.sleep(0.2)
            election = Election(self.id, self.groupView, self.leaderID, self.Leader, self.isElection, self.participation,self.lock,None )
            election.start()
            #election.join()
                # start the election
        elif self.leaderID.value != -1: # mean not None
            logger.debug("Node:{}, leader already exist, starting ping module for this node...")
            self.isElection.value = 0
            
            broad_cast = multiprocessing.Process(target=recv_ping, args = (self.id,37020, self.broadcaster, self.groupView,self.leaderID,self.Leader,self.participation,self.isElection, self.lock))
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
            