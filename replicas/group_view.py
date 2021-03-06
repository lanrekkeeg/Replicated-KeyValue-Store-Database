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

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('test')

class GroupView(multiprocessing.Process):
    def __init__(self, id ,port, meta):
        super(GroupView, self).__init__()
        self.meta = meta
        self.id = id
        self.send_multicast = MulticastSend(self.id)
        self.recv_multicast = MulticastRec(self.id)
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
    
    def check_incoming_multicast_message(self):
        while True:
            try:
                data, addr = self.recv_multicast.sock.recvfrom(1024)
                message = data.decode()
                message = json.loads(message)
                if message.get('oper',None) == "groupview":
                    print ('Data = %s' % message['message'])

            except socket.error as e:
                print ('Expection:{}'.format(e))
        