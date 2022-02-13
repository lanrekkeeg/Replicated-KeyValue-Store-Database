
from os import extsep
import socket
import multiprocessing
import sys
#import global_conf as glob_var
import logging
from util import *
import json
import datetime
from broad_multi_cast import MulticastSend, MulticastRec
from broadcast import *
import time
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('test')

#groupview = {1:'127.0.0.1:9001',2:'127.0.0.1:9002',3:'127.0.0.1:9004',4:'127.0.0.1:9005',5:'127.0.0.1:9006',6:'127.0.0.1:9007'}

import socket
from bully_election import Election

class CareTakerServer(multiprocessing.Process):
    def __init__(self, id, client_conn, client_addr,program_order, groupView, groupViewReplica, leaderID, Leader, isElection, participation, lock,sqn):
        super(CareTakerServer, self).__init__()
        self.groupViewReplica = groupViewReplica
        self.program_order = program_order
        self.groupView = groupView
        self.leaderID = leaderID
        self.Leader = Leader
        self.isElection = isElection
        self.participation = participation
        self.client_conn = client_conn
        self.client_addr = client_addr
        self.id = id
        self.multicast_send = MulticastSend(self.id)
        self.multicast_rec = MulticastRec(self.id)
        
        self.broad_send = BroadcastSender(self.id)
        self.broad_recv = BroadcastRecev()
        
        self.lock = lock
        self.sqn = sqn
    # Override run method
    
    # not use  because of python multiprocessing share object synchronization
    def get_sqn_for_program_order(self, client_uuid):
        """
        return sqn number 
        """
        while not self.program_order['order']['status']:
            time.sleep(0.00005)
        
        self.lock.acquire()
        order = self.program_order['order']
        sqn = order[client_uuid]['sqn']
        order.pop(client_uuid)
        self.lock.release()
        return sqn
            
    # not use  because of python multiprocessing share object synchronization
    def add_sqn_request_to_queu(self,client_uuid):
        """
        """
        self.program_order.acquire()
        order_ = self.program_order['order']
        if client_uuid in order_.keys():
            logger.error("client id already exist in queue...")
            self.program_order.release()
            return 0
        order_[client_uuid] = {'status':False,'sqn':None}
        self.program_order['order'] = order_
        self.program_order.release()
        return 1
        
    # not use  because of python multiprocessing share object synchronization # seperate process 
    def allocate_sqn_via_program_order(self):
        """
        allocating sqn number to client by respecting program order
        """
        logger.info("Sending request for sqn number, if it is new leader .....")
        ts_now = datetime.datetime.now()
        ts_new = datetime.datetime.now()
        while (ts_new-ts_now).total_seconds() <= 5 and self.sqn.value == -1:
            """
            check with replica
            """
            message = {"nodeID":self.id,"oper":"status","message":{"status":"sqn_no"}}
            self.multicast_send.broadcast_message(message)
            ts_new = datetime.datetime.now()
            time.sleep(0.3)
        
        if self.sqn.value == -1:
            logger.error("Fail to communicate with replica")
            return -1
        logger.info("Sending sqn number to handler")
        #self.multicast_send.sock.close()
        while True:
            # parse it
            try:                
                self.lock.acquire()
                order = self.program_order['order']

                for key, data in order.items():
                    order[key]['status'] = True
                    order[key]['sqn'] = self.sqn.value
                    self.sqn.value += 1
                self.program_order['order'] = order
                self.lock.release()
            except Exception as exp:
                logger.error("Exception in sqn allocation process,{}".format(exp))
            time.sleep(0.01)
        
    def get_sqn_number(self):
        """
        """
        logger.info("Sending request for sqn number, if it is new leader .....")
        ts_now = datetime.datetime.now()
        ts_new = datetime.datetime.now()
        while (ts_new-ts_now).total_seconds() <= 5 and self.sqn.value == -1:
            """
            check with replica
            """
            message = {"multicast":True, "nodeID":self.id, "replica_message":"1","oper":"status","message":{"status":"sqn_no"}}
            self.broad_send.broadcast_message(message)
            ts_new = datetime.datetime.now()
            time.sleep(0.3)
        
        if self.sqn.value == -1:
            logger.error("Fail to communicate with replica")
            return -1
        
        logger.info("Sending sqn number to handler")
        #self.multicast_send.sock.close()
        self.lock.acquire()
        val = self.sqn.value
        self.sqn.value += 1
        self.lock.release()
        return  val
        
    def check_response(self, sqn):
        """
        """
        ts_now = datetime.datetime.now()
        ts_new = datetime.datetime.now()
        while (ts_new-ts_now).total_seconds()<=5:
            ts_new = datetime.datetime.now()
            data, addr= self.broad_recv.broad_cast_receiver.recvfrom(1024)
            try:
                data = data.decode()
                data = json.loads(data)
                if check_multicast(data):
                    if data.get('oper', None) == "response":
                        if data.get("sqn_no",None) is not None:
                            if data.get("nodeID",None) == self.id and data.get("sqn_no") == sqn:
                                logger.info("sending response to client")
                                return data
            except Exception as exp:
                logger.error("In response, Got {}".format(exp))
        message = {"nodeID":  self.id, "oper": "response", "message": {"success": 0, "data": "Failed to perform request"}}
        return message
            
    def run(self):
        logger.debug("Node:{},process is spawn for new client".format(id))
        # Message to be sent to client
        while True:
            # Receive message from client
            try:
                data = self.client_conn.recv(1024)
                if not data:
                    logger.warning("Breaking client socket as connection close from client side")
                    break
            except Exception as exp:
                logger.info("Closing socket")
                return
            
            data = data.decode()
            print("Node:{},Recevied message from client, message is {}".format(self.id, data))
            try:
                data = json.loads(data)
            except Exception as exp:
                logger.error("Failed to pared json data,{}".format(exp))
                continue
            if data.get("acquire",None) is not None:
                if self.Leader.value:
                    message = {"isLeader":1}
                else:
                    message = {"isLeader":0}
                message = json.dumps(message)
                message = str.encode(message)
                self.client_conn.send(message)
                
            elif data.get('oper') == 'election':
                msg = data['message']
                if msg['ElectionStatus'] == 'running':
                    logger.info("Node:{}, receive messagem from election".format(self.id))
                        # start election, by passing the client socket if available
                    message = {'nodID': self.id, 'oper': 'election', 'message':{'ElectionStatus':'running','ack': True}}
                    message = json.dumps(message)
                    message = str.encode(message)
                    self.client_conn.send(message)
                    if not self.participation.value:
                        elec = Election(self.id, self.groupView, self.leaderID, self.Leader,self.isElection,self.participation,self.lock,self.client_conn)
                        elec.start()
                    self.client_conn.close()
                    
                #################### MAIN LOGIC ####################

            elif self.Leader.value and check_multicast(data): # ignore message mixing
                
                
                sqn = self.get_sqn_number()
                if sqn == -1:
                    message = {"nodeID":  self.id, "oper": "response", "message": {"success": 0, "data": "Failed to perform request"}}
                    message = encode_message(message)
                    self.client_conn.send(message)
                
                else:

                    logger.info("sqn_number is: {}".format(sqn))
                    time_ = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
                    #message = {"id":"clien_1","send_time": time_,"oper": "key-value", "message":{"oper-type": "write", "bucket_name":"db","content":{"class":"8:00","type":"MS"}, "sqn_no":sqn_}}
                    data['nodeID'] = self.id
                    data['send_time'] = time_
                    data['message']['sqn_no'] = sqn
                    logger.info("Sending message to replica manager...")
                    self.broad_send.broadcast_message(data)
                    logger.info("Waiting for response...")
                    message = self.check_response(sqn)
                    #logger.debug("Data from client: {}".format(data))
                    #message = {"nodeID":self.id, "oper": "key-valye","message":{"response":"hell wordl from "+ str(self.id)}}
                    #message = json.dumps(message)
                    #message = str.encode(message)
                    message = encode_message(message)
                    self.client_conn.send(message)
                    logger.info("Sending Response to client....")
            else:
                self.client_conn.close()
                return
    
class ClientHandler(multiprocessing.Process):

    def __init__(self, id, ip, port,program_order, groupView, groupViewReplica,leaderID, Leader, isElection, participation, loc, sqn):
        super(ClientHandler, self).__init__()
        self.groupViewReplica=groupViewReplica
        self.program_order = program_order
        self.groupView = groupView
        self.leaderID = leaderID
        self.Leader = Leader
        self.isElection = isElection
        self.participation = participation
        self.id = id
        self.port = port
        self.ip = ip
        self.lock = loc
        self.sqn = sqn

    def run(self):
        logger.debug("Node:{},Client Handlers is started ...".format(id))
        # Create a UDP socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Server application IP address and port
        server_address = self.ip
        server_port = self.port
    
        # Buffer size
        buffer_size = 1024
    
        # Bind socket to address and port
        try:
            server_socket.bind((server_address, server_port))
            logger.debug("Starting server at...")
        except Exception as exp:
            logger.error("Failed to start the client server, {}".format(exp))
        logger.debug('Node:{},ClientHandler Server Up and Running.... {}:{}'.format(id,server_address, server_port))
        
        server_socket.listen()
        
        while True:
            # Receive message from client
            try:
                conn, addr = server_socket.accept()
                logger.info ('######################## {} ################'.format(addr))
            except Exception as exp:
                logger.error("Got error while connecting to client,error is: {}".format(exp))
            #data, address = server_socket.recvfrom(buffer_size)
            #print('Received message \'{}\' at {}:{}'.format(data.decode(), address[0], address[1]))
            # Create a server process
            p = CareTakerServer(self.id, conn,addr, self.program_order,self.groupView,self.groupViewReplica, self.leaderID, self.Leader, self.isElection, self.participation, self.lock,self.sqn)
            #p.daemon = True
            p.start()
            #p.join()
        