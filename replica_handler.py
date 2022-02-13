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
from broadcast import *
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('test')

class ReplicaHandler(multiprocessing.Process):
    def __init__(self, id,isLeader,groupview, sqn, port,lock):
        super(ReplicaHandler, self).__init__()
        self.port = port
        self.host =  get_ip()#socket.gethostbyname(socket.gethostname())
        self.isLeader = isLeader
        self.groupView = groupview
        self.sqn_no = sqn
        self.id = id
        self.lock = lock
        self.send_multicast = MulticastSend(self.id)
        self.recv_multicast = MulticastRec(self.id)
        self.send_broadcast = BroadcastSender(self.id)
        self.recv_broadcast = BroadcastRecev()
        
        
    # Override run method
    def run(self):
        logger.info("Group view process started, listenting for replica operation and maintaining group view for replicas")
        # Message to be sent to client
        '''
        Basic structure of replicas
         groupview incoming message = {"nodeID":1,2,4,"oper":"groupView","message":{"host:"abc", "status":"ready, pending, dead"}}
        '''
        rebalance = multiprocessing.Process(target=self.rebalance_group_view)
        rebalance.start()
        logger.info("Replication handler started.....")
        while True:
            try:
                data, addr = self.recv_broadcast.broad_cast_receiver.recvfrom(1024)
                message = data.decode()
                message = json.loads(message)
                #logger.info("*************message received************")
                if check_multicast(message):
                    if message.get('oper',None) == "groupView":
                        self.update_group_view(message)
                    
                    if message.get("oper",None) == "response":
                        #logger.info(message)
                        #logger.info("{},{}".format(type(message['to']),type(self.id)))
                        if message['message'].get("sqn_no",None) is not None and message.get("to",None) == self.id:
                            self.update_sqn_no(message)
                    
            except Exception as e:
                logger.error("Got exception while handling incoming data error is, {}".format(str(e)))
    
    def update_sqn_no(self, message):
        """
        update sequence number which is received from replica handler
        """
        logger.info("Updating sqn no which is received from replica: {}".format(message['nodeID']))
        sqn_no = message['message']['sqn_no'] + 1
        self.lock.acquire()
        self.sqn_no.value = sqn_no
        self.lock.release()
        
    def multicast_sqn(self, id): 
        """
        """
        logger.info("sending sqn number to replica manager: {}".format(id))
        message = {"multicast":True,"nodeID":self.id,"oper": "status","message":{"success":1, "sqn":self.sqn.value}}
        self.send_broadcast.broadcast_message(message)
        
    def multicast_leader(self):
        """
        """
        if self.isLeader.value:
            message = {"multicast":True,"oper":"response","message":{"leader":self.id,"host":self.host,"port":self.port}}
            self.send_broadcast.broadcast_message(message)
        

    def update_group_view(self, data):
        """
        updating group view
        """
        time_ = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        logger.info('Groupview data is, {}'.format(data))
        temp_dict = self.groupView['groupView']
        temp_dict.update({data['nodeID']: {"host":data['message']['host'], "status":data['message']['status'],"lastcheck":time_}})
        self.groupView['groupView'] = temp_dict
        logger.debug("updated group view is,{}".format(self.groupView['groupView']))
       
    def rebalance_group_view(self):
        """
        removing unused node
        """
        logger.info("Rebalance process started...")
        while True:
            # parse it
            try:
                curr_time = datetime.datetime.now() 
                
                group_view_temp = self.groupView['groupView']
                for key, data in group_view_temp.items():
                    if group_view_temp[key]['status'] != "dead":
                        last_active_time = group_view_temp[key]['lastcheck']
                        last_active_time = datetime.datetime.strptime(last_active_time,"%m/%d/%Y, %H:%M:%S")
                        diff = curr_time - last_active_time
                        diff = diff.total_seconds()
                        if diff > 2: # to call off for election
                            logger.warning("Replica manager [{}] found dead,updating groupview status".format(key))
                            data['status'] = "dead"
                            self.lock.acquire()
                            temp_grp = self.groupView['groupView']
                            temp_grp[key]['status'] = "dead"
                            self.groupView['groupView'] = temp_grp
                            self.lock.release()
                            logger.info("**********group view:{} ****************".format(self.groupView['groupView']))
            except Exception as exp:
                logger.error("Exception in rebalance process,{}".format(exp))
            time.sleep(2)
                