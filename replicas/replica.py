from os import times, write
from broad_multi_cast import MulticastRec, MulticastSend
import logging
import multiprocessing
from multiprocessing import Manager
import sys
from queue import Queue
import time
from database_Oper import *
import copy
from tinydb import TinyDB, Query
import pickle
import datetime
from replica_handler import ReplicaHandler
from startup_routine import Startup_Routine
from broadcast import *
from  pathlib import Path

logging.basicConfig(level=logging.DEBUG)
global id

logger = logging.getLogger("replica-manager")
import json

class Replica(multiprocessing.Process):
    def __init__(self, groupView, response_queu, hold_back_queu, sqn_no,is_ready, id, switch):
        super(Replica, self).__init__()
        self.id = id
        self.hold_back_Queue = hold_back_queu
        self.hold_back_Queue_sqn = sqn_no
        self.response_queue = response_queu
        #self.isPrimary = None
        self.groupView = groupView
        self.is_ready = is_ready
        self.muticast_send = MulticastSend(self.id)
        self.muticast_recv = MulticastRec(self.id)
        
        self.send_broadcast = BroadcastSender(self.id)
        self.recv_broadcast = BroadcastRecev()
        self.switch = switch
        #from database_Oper import db_buckets
        if not self.switch:
            pass
            #self.var = db_buckets
            #self.db_object = load_all_buckets()
        
    def run(self):
    
        # adding is alive check to avoid reading its own dump
        while not self.is_ready.value:
            time.sleep(1)
            continue
            
        if self.switch:
            #response = multiprocessing.Process(target=self.check_response_queu(self.response_queue,))
            #response.start()
            self.check_response_queu()
        else:
            self.receive()
            
    def send_response(self):
        pass
    
    def dump_hold_back_queue(self):
        """
        """
        logger.debug("Dumping holdback queue")
        hld_que = self.hold_back_Queue[:]
        hld_que.append({"sqn_no":self.hold_back_Queue_sqn.value})
        
        try:
            open('db_hld_queue/hld.data', 'wb')
        except Exception as exp:
            logger.info("creating dump file for writing")
            file = Path('db_hld_queue/hld.data')
            file.touch(exist_ok=True)
            
        with open('db_hld_queue/hld.data', 'wb') as handle:
            # store the data as binary data stream
            pickle.dump(hld_que, handle)
        logger.debug("hold back queue dump successfully...")
        #print(self.hold_back_Queue)

        
    
    
    def receive(self):
        logger.info("starting receving process")
        while True:
            data, addr = self.recv_broadcast.broad_cast_receiver.recvfrom(1024)
            message = data.decode()
            message = json.loads(message)
            #logger.debug("Received request, adding into hold_back_queu...")
            if check_multicast(message):
                if message['oper'] == "key-value": # need to check
                    message['timestamp'] = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    
                    logger.debug("Adding record in hold back queue")
                    add_record(cordinator_logs['logs'], message )
                    # discard duplicates e.g curr_sqn = 12, upcoming is 11 then we need to discard it
                    self.hold_back_Queue.append(message)
                    self.dump_hold_back_queue()
                    self.deliver()
    
    def deliver(self):
        popping_index = []
        iter = 0
        #print("len is ", len(self.hold_back_Queue))
        while iter < len(self.hold_back_Queue):
            # in_sqn = curr_sqn(+1)
            if self.hold_back_Queue[iter]['message']['sqn_no'] == (self.hold_back_Queue_sqn.value+1):
                logger.info("Message with sqn no {} and send time {} is delived".format(self.hold_back_Queue_sqn.value,self.hold_back_Queue[iter]['send_time']))
                self.hold_back_Queue_sqn.value +=1
                msg = self.hold_back_Queue.pop(iter) #self.hold_back_Queue[iter]
                #msg['oper'] = "response"
                #msg['message'] = {"isresponse":1,"response":200, "result":"success"}
                #self.response_queue.append(msg)
                self.key_value_operation(msg)
                iter = 0
                self.dump_hold_back_queue()
                continue
            # to remove duplicates
            elif self.hold_back_Queue[iter]['message']['sqn_no'] <= self.hold_back_Queue_sqn.value:
                self.hold_back_Queue.pop(iter) #self.hold_back_Queue[iter]
                logger.debug("discarding duplicates..")

            iter +=1
        
    def key_value_operation(self, message):
        """
        perform key value operation over the underlying json store
        response {"success":1 or 0, "error":"if response is 0", "data":"db data"}
        """
        original_message = copy.deepcopy(message)
        db_operation = message['message']['oper-type']
        db_bucket = message['message']['bucket_name']
        db_content = message['message']['content']
        if db_bucket not in list(db_buckets.keys()):
            logger.info("unable to find specified bucket")
            error = "unable to find bucket with name:"+db_bucket
            response = {"success":0, "error":error}
            message['message'] = response
            message['oper'] = "response"
            self.response_queue.append(message)
            return
        
        response = {"success":1, "data":None}
            
        logger.debug("response init is :{}".format(response))

        if db_operation == "write":
            resp = add_record(db_buckets[db_bucket],db_content)
        elif db_operation == "deletebyID":
            resp = delete_by_id(db_buckets[db_bucket], db_content['id'])
        elif db_operation == "searchbyID":
            resp = search_by_id(db_buckets[db_bucket],db_content['id'])
        elif db_operation == "searchbyQuery":
            pass
        elif db_operation == "updatebyID":
            resp = update_by_id(db_buckets[db_bucket],db_content)
        elif db_operation == "updatebyQuery":
            pass
        elif db_operation == "createBucket":
            pass
            
        
        # sending record back to client
        
        response["data"] = resp
        logger.debug("response is :{}".format(response))
        message['message'] = response
        message['oper'] = "response"
        message['sqn_no'] = original_message['message']['sqn_no']
        message['nodeID'] = original_message['nodeID']
        message['multicast'] = True
        
        self.response_queue.append(message)
        logger.debug("response is :{}".format(message))
        #logger.debug("Response queue is:{}".format(self.response_queue))
        self.write_to_disk(original_message)
        return
        # add data
        # delete data
        # get data
        
                
    def write_to_disk(self, message):
        """
        write operation to disk
        """
        add_record(db_operation['operations'],message)
        logger.debug("commiting disk operation to disk....")
    
    def check_response_queu(self):
        """
        check for new responsed and send it back to client
        """
        print("Starting response process....")
        while True:
            try:
                msg = self.response_queue.pop()
                self.send_broadcast.broadcast_message(msg)
                logger.info("sending response back to {}".format(msg['nodeID']))
            except Exception as exp:
                #logger.info("Got error while sending response to client..., {}".format(exp))
                #logger.info("Holdback queue is:{}".format(self.response_queue))
                #logger.info("Holdback queue sqn no is :{}".format(self.hold_back_Queue_sqn))
                
                time.sleep(0.2)
                pass
                #print("response Queue is empy..")
                

if __name__ == "__main__":

    manager = Manager()
    id = int(sys.argv[1])
    is_ready = manager.Value('i', 0)
    groupView = manager.dict({'groupView':{}})
    hold_back_queue = manager.list([])
    response_queue = manager.list([])
    sqn_no = manager.Value('i',0)
    lock = manager.Lock()
    R_s = Replica(groupView, response_queue, hold_back_queue, sqn_no,is_ready, id,1)
    R_r = Replica(groupView, response_queue, hold_back_queue, sqn_no,is_ready, id,0)
    R_hand = ReplicaHandler(id,is_ready,lock, sqn_no)
    R_r.start()
    R_s.start()
    R_hand.start()
    time.sleep(3)
    start_routine = Startup_Routine(id, sqn_no,hold_back_queue, is_ready)
    R_r.join()
    R_s.join()
    R_hand.join()
    