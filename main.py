from multiprocessing import Manager
from replica_handler import ReplicaHandler
import sys
import logging
from util import *
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('test')

import time
from client_handler import ClientHandler
from broadcast import  Broadcaster
from startup_routine import Startup_Routine
from group_view import GroupView        
import socket
import signal
import sys
signal.signal(signal.SIGTERM, lambda signum, stack_frame: sys.exit(1))

if __name__ == '__main__':
    # 1. start group view process
    # 2. start sockets (also needed for election Process and other operation) 
    # 3. start election process
    # 4. Incase of victory, start serving the request
    # 5. Incase of victory start broadcasting health
    # 6. Incase of failure start ping module to monitor leader health
    # 7. Future start file syncher 
    logger.debug("Starting Servers .....")
    manager = Manager()

    groupView = manager.dict({'groupView':{}})
    groupViewReplica = manager.dict({'groupView':{}})
    program_order = manager.dict({'order':{}})

    sqn = manager.Value('i', -1)
    leaderID =  manager.Value('i', -1)
    Leader = manager.Value('i', 0) # either 0 or 1
    isElection = manager.Value('i', 0) # either 0 or 1
    participation = manager.Value('i', 0) # either 0 or 1
    lock_rep = manager.Lock()
    
    #global id
    #global port
    id = sys.argv[1]
    port = int(sys.argv[2])
    
    broad = Broadcaster(id, groupView, leaderID, Leader, isElection, participation, port, lock_rep, sqn)
    clients = ClientHandler(id,get_ip(), port, program_order,groupView,groupViewReplica, leaderID, Leader, isElection,participation,lock_rep,sqn)
    view = GroupView(id,port,groupView, leaderID, Leader)
    replicaHandler = ReplicaHandler(id,Leader,groupViewReplica,sqn,port,lock_rep)
    #replicaHandler.daemon = True
    replicaHandler.start()
    #broad.daemon = True
    
    broad.start()
    #clients.daemon = True
    clients.start()
    #view.daemon = True
    view.start()
    
    routine = Startup_Routine(id,groupView, leaderID, Leader, isElection, participation,lock_rep)
    time.sleep(1) # to give  time to form group view
    
   
    
    broad.join()
    view.join()
    clients.join()
    replicaHandler.join()
    
    
    
    
    
    