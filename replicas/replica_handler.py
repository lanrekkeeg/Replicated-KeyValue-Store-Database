import socket
import multiprocessing
from multiprocessing import Manager
import time
from broad_multi_cast import MulticastSend, MulticastRec
#import global_conf as glob_var
import logging
from util import *
import json
import datetime
from util import *
from database_Oper import *
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('test')

class ReplicaHandler(multiprocessing.Process):
    def __init__(self, id,isReady,lock):
        super(ReplicaHandler, self).__init__()
        self.host = socket.gethostbyname(socket.gethostname())
        self.isReady = isReady
        self.id = id
        self.lock = lock
        self.send_multicast = MulticastSend(self.id)
        self.recv_multicast = MulticastRec(self.id)

        
        
    # Override run method
    def run(self):
        logger.info("Replica Fault tolerant started ...")
        # Message to be sent to client
        '''
        Basic structure of replicas
         groupview incoming message = {"nodeID":1,2,4,"oper":"groupView","message":{"host:"abc", "status":"ready, pending, dead"}}
        '''
       
        logger.info("Replication handler started.....")
        while True:
            try:
                data, addr = self.recv_multicast.sock.recvfrom(1024)
                message = data.decode()
                message = json.loads(message)
                #logger.info("*************message received************") 
                if message.get("oper",None) == "status":
                    if message['message'].get("status",None) == "sqn_no":
                        logger.info("status data is, {}".format(message['message']))
                        self.multicast_sqn(message['nodeID'])
            except Exception as e:
                logger.error("Got exception while handling incoming data error is, {}".format(str(e)))
    
    def multicast_sqn(self, id): 
        """
        """
        sorted_history = sort_dict(cordinator_logs['logs'].all())
        if len(sorted_history)!=0:
            sqn = sorted_history[0]['message']['sqn_no']
        else:
            sqn = 0
        logger.info("sending sqn number to replica manager: {}".format(id))
        message = {"nodeID":self.id,"oper": "response","message":{"success":1, "sqn_no":sqn}}
        self.send_multicast.broadcast_message(message)
        
 

    
                