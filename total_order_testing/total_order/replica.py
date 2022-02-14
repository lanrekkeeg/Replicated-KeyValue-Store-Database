from broad_multi_cast import MulticastRec, MulticastSend
import logging
import multiprocessing
from multiprocessing import Manager
import sys

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('replica-manager')
import json

class Replica(multiprocessing.Process):
    def __init__(self, groupView, response_queu, hold_back_queu, sqn_no,is_ready, id):
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

        
    def run(self):
        self.receive()
        
    def send_response(self):
        pass
    
    def receive(self):
        logger.info("starting receving process....")
        while True:
            data, addr = self.muticast_recv.sock.recvfrom(1024)
            message = data.decode()
            message = json.loads(message)
            #logger.debug("Received request, adding into hold_back_queu...")
            self.hold_back_Queue.append(message)
            self.deliver()
    
    def deliver(self):
        popping_index = []
        iter = 0
        #print("len is ", len(self.hold_back_Queue))
        while iter < len(self.hold_back_Queue):
            if self.hold_back_Queue[iter]['message']['sqn_no'] == self.hold_back_Queue_sqn.value:
                logger.info("Message with sqn no {} and send time {} is delived".format(self.hold_back_Queue_sqn,self.hold_back_Queue[iter]['send_time']))
                self.hold_back_Queue_sqn.value +=1
                iter = 0
                continue
            iter +=1
                
        
    
    def update_response_queu(self):
        pass

if __name__ == "__main__":
    manager = Manager()
    id = int(sys.argv[1])
    is_ready = manager.Value('i', 0)
    groupView = manager.dict({'groupView':{}})
    hold_back_queue = manager.list([])
    response_queue = manager.list([])
    sqn_no = manager.Value('i',0)
    R = Replica(groupView, response_queue, hold_back_queue, sqn_no,is_ready, id)
    R.start()
    R.join()

    