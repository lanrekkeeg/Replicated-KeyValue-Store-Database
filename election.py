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
    sqn = manager.Value('i', 0)
    leaderID =  manager.Value('i', -1)
    Leader = manager.Value('i', 0) # either 0 or 1
    isElection = manager.Value('i', 0) # either 0 or 1
    participation = manager.Value('i', 0) # either 0 or 1
    lock_rep = manager.Lock()
    
    #global id
    #global port
    id = sys.argv[1]
    port = int(sys.argv[2])
    
    broad = Broadcaster(id, groupView, leaderID, Leader,isElection ,participation, lis=1)
    broad2 = Broadcaster(id, groupView, leaderID, Leader,isElection, participation, lis=0)
    clients = ClientHandler(id,'127.0.0.1', port, groupView, leaderID, Leader, participation, isElection)
    view = GroupView(id,port,groupView, leaderID, Leader)
    replicaHandler = ReplicaHandler(id,Leader,groupViewReplica,sqn,lock_rep)
    replicaHandler.start()
    broad.start()
    broad2.start()
    clients.start()
    view.start()
    
    routine = Startup_Routine(id,groupView, leaderID, Leader, isElection, participation)
    time.sleep(1) # to give  time to form group view
    
    # check for leader
    
    #if isElection:
    #    elc = Election(id)
    #    elc.start()
    
    '''
    

    '''
   
    
    broad.join()
    broad2.join()
    view.join()
    clients.join()
    replicaHandler.join()


    #elc.join()

    
    
    # wait for some time
    # send election message that election is started
    #process.append(multiprocessing.Process(target=broad.listen_to_broadcast_message, args=()))
    #process.append(multiprocessing.Process(target=broad2.broad_cast_message, args=()))

    #for proc in process:
        #proc.daemon = True

        #proc.start()
        #proc.join()
    
    
    
    