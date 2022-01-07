
import logging
from util import *
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('test')
import datetime
from broad_multi_cast import *
import pickle

class Startup_Routine(object):
    def __init__(self,id,sqn_no,hld_back, is_alive):
        '''
            1. check for the leader
            2. if there is leader, then check if it is legal leader
            3. if not legal leader then start the election
            
            if not self.find_leader():
                start the election process
            else if self.find_leader():
                check node id, if smaller then bully and start the election
        '''
        self.hold_back_queue = hld_back
        self.id = id
        self.is_alive = is_alive
        self.sqn_no = sqn_no
        self.multicast_send = MulticastSend(id)
        self.multicast_rec = MulticastRec(id)
        self.multicast_rec.sock.settimeout(10)
        self.load_hold_back_queu()
        self.is_alive.value = 1
        self.start_routine()
        
        
    
    def close_sock(self):
        """
        close both sender and rec
        """
        self.multicast_send.sock.close()
        self.multicast_rec.sock.close()
        
    def wait_for_reply(self):
        """
        collect all sqn number within 10 sec time window
        """
        ts_now = datetime.datetime.now()
        ts_new = datetime.datetime.now()
        sqn_list = []
        while (ts_new-ts_now).total_seconds()<=10:
            try:
                data, addr= self.multicast_rec.sock.recvfrom(1024)
                data = data.decode()
                data = json.loads(data)
                if data.get('oper', None) == "response":
                    if data['message'].get("sqn_no",None) is not None:
                        sqn_list.append((data['nodeID'],data['message']['sqn_no']))  
            except socket.error as exp:
                logger.error("In one of the response, Got {}".format(exp))
            ts_new = datetime.datetime.now()

            
        logger.info("Collected sequence number are: {}".format(sqn_list))
        return sqn_list
    
    def load_hold_back_queu(self):
        """
        loading holdback queue
        """
        logger.info("Loading holdback Queue Dump")
        hld_que = []
        try:
            with open('db_hld_queue/hld.data', 'rb') as handle:
                # store the data as binary data stream
                hld_que = pickle.load(handle)
        except Exception as exp:
            logger.error("Failed to load hld_que dump..")
            return 
        sqn_record = hld_que.pop(-1)
        self.sqn_no.value = int(sqn_record['sqn_no'])
        self.hold_back_queue = hld_que
        logger.info("From hold back queue dump sqn no:{} is loaded".format(self.sqn_no.value))
        
        
        
    def start_routine(self):
        """
        1. send broadcasr
        2. collect all latest sequence number
        """
        logger.info("Startup Routine Started .....")
        message = {"nodeID":self.id,"oper":"status","message":{"status":"sqn_no"}}
        self.multicast_send.broadcast_message(message)
        sqn_list = self.wait_for_reply()
        #logger.info("type",type(sqn_list[0][0]),type(self.id))
        # local sqn number
        if len(sqn_list) == 0:
            # i am only alive, start the process
            logger.info("Receive no reply from any client assuming to be the 1st")
            self.close_sock()
            return
        elif len(sqn_list) == 1 and sqn_list[0][0] == self.id:
            logger.info("Receive self reply from any client assuming to be the 1st")
            self.close_sock()
            return
        else:
            sorted_by_sqn = sorted(sqn_list, key=lambda tup: tup[1],reverse=True)
            message = {"requested_replica":sorted_by_sqn[0][0],"oper":"recovery","message":{"oper":"recovery","from_sqn":self.sqn_no.value}}
            self.multicast_send.broadcast_message(message)
            self.close_sock()
            
        logger.info("Startup Routine Finished....")
            
        