import socket
import multiprocessing
#import global_conf as glob_var
import logging
from util import *

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('test')


import socket
import time
from broadcast import BroadcastSender

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
        host = None
        while 1:
            host = socket.gethostbyname(socket.gethostname())
            if host != '127.0.0.1' or host != 'localhost':
                break
            
        while True:
            message = {'oper': 'groupview','nodeID':self.id, 'message':{'host':host,'port':self.port}}
            self.broadcaster.broadcast_message(message)
            time.sleep(0.3)