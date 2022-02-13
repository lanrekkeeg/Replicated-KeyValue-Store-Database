import socket
import multiprocessing
from multiprocessing import Manager
import time
from broad_multi_cast import MulticastSend, MulticastRec
#import global_conf as glob_var
import logging
from util import *
import json
from util import *
from database_Oper import *
from broadcast import *
from util import *
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('test')

class ReplicaHandler(multiprocessing.Process):
    def __init__(self, id,isReady,lock, sqn):
        super(ReplicaHandler, self).__init__()
        self.host = get_ip() #socket.gethostbyname(socket.gethostname())
        self.isReady = isReady
        self.id = id
        self.lock = lock
        self.sqn = sqn
        self.send_multicast = MulticastSend(self.id)
        self.recv_multicast = MulticastRec(self.id)
        
        self.send_broadcast = BroadcastSender(self.id)
        self.recv_broadcast = BroadcastRecev()
        
        

        
        
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
                data, addr = self.recv_broadcast.broad_cast_receiver.recvfrom(1024)
                message = data.decode()
                message = json.loads(message)
                
                #logger.info("*************message received************")
                if check_multicast(message):
                    logger.debug("Data receive by handler:{}".format(message))
                    if message.get("oper",None) == "status":
                        if message['message'].get("status",None) == "sqn_no": # and message.get("to",None) == self.id:
                            logger.info("status data is, {}".format(message['message']))
                            self.multicast_sqn(message['nodeID'])
                            
                    elif message.get("oper",None) == "recovery":
                        if message.get("requested_replica",None) == self.id:
                            """
                            starting
                            """
                            self.recovery_process(message)
                    
            except Exception as e:
                logger.error("Got exception while handling incoming data, error is, {}".format(str(e)))
    
    def multicast_sqn(self, id): 
        """
        """
        sorted_history = sort_dict(cordinator_logs['logs'].all())
        if len(sorted_history)!=0:
            sqn = sorted_history[0]['message']['sqn_no']
        else:
            sqn = 0
        logger.info("sending sqn number to replica manager: {}".format(id))
        message = {"multicast":True,"nodeID":self.id, "to":id,"oper": "response","message":{"success":1, "sqn_no":sqn}}
        self.send_broadcast.broadcast_message(message)
        
    def recovery_process(self, message):
        """
        """
        logger.info("Starting recovery service....")
        from_sqn = message['message']['from_sqn']
        q = Query()
        self.lock.acquire()
        local_sqn = self.sqn.value
        self.lock.release()

        data = cordinator_logs['logs'].search(q.message.sqn_no > int(from_sqn))
        for record in data:
            """
            """
            if record['message']['sqn_no'] <= local_sqn:
                self.send_broadcast.broadcast_message(record)
        
        logger.info("Finish sending record from {} to {} sqn".format(from_sqn, local_sqn))
        
        
 

    
                