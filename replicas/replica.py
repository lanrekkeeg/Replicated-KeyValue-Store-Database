from broad_multi_cast import MulticastRec, MulticastSend
import logging
import multiprocessing
from multiprocessing import Manager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('replica-manager')
import json

class Replica(multiprocessing.Process):
    def __init__(self, meta, id):
        super(Replica, self).__init__()
        self.id = id
        self.hold_back_Queue = []
        self.hold_back_Queue_sqn = 0
        self.response_queue = []
        #self.isPrimary = None
        self.groupView = None
        self.muticast_send = MulticastSend(self.id)
        self.muticast_recv = MulticastSend(self.id)

        pass
    def run(self):
        pass
    def send_response(self):
        pass
    
    def recieve(self):
        logger.info("starting receving process....")
        while True:
            data, addr = self.muticast_recv.sock.recvfrom(1024)
            message = data.decode()
            message = json.loads(message)
            self.hold_back_Queue.append(message)
            self.deliver()
    
    def deliver(self):
        
        pass
    
    def update_response_queu(self):
        pass

if __name__ == "__main__":
    manager = Manager()

    groupView = manager.dict({'groupView':{}})
    holb_back_queue = manager.dict({'hld_queue':{}})
    response_queue = manager.dict({'hld_queue':{}})
    sqn_no = manager.Value('i',0)

    