import socket
import multiprocessing
from multiprocessing import Manager
import sys
#import global_conf as glob_var
import logging
from util import *
import json
import datetime
import platform
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('test')

import socket
import time

def recv_ping(id,port, broad_caster, groupView, leaderID, Leader, participation,isElection, lock):
    
    """
    Check for health
    1. store time called last time
    2. rece broadcast message after id/max_id + 1 sec
    3. if message rec then check last time
    4. else send election notification
    """
    logger.info("XXXXXXXXXXXXXXXXX Starting Ping Service XXXXXXXXXXXXXXXX")

    broad_cast_receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
    broad_cast_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    if platform.system() != 'Windows':
        broad_cast_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    #broad_cast_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    #broad_cast_sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    # Enable broadcasting mode
    #broad_cast_sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    broad_cast_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    broad_cast_receiver.bind(("", port))
    last_time = datetime.datetime.now() 
    while not isElection.value:
        data, addr = broad_cast_receiver.recvfrom(1024)
        # parse it
        curr_time = datetime.datetime.now() 

        data = data.decode()
        data = json.loads(data)
        
        if data.get('ping') is not None:
            last_time = curr_time
            #current_ping =  current ping time
            # check time diff
            # if voilates
            # wait for t second
            # check election
        diff =  curr_time - last_time
        #logger.info("Node:{}, time diff for ping message is {} and message is {}".format(id, diff, data))
        #logger.info("Ping message is {}".format(data))

        diff = diff.total_seconds()
        if diff > 3: # to call off for election
        
            # check if election is already started?
            # broadcast message for election
            # if not then start the election
            logger.info("$$$$$$$$$$$$$$ Leader Found Dead $$$$$$$$$$$$")
            message = {"nodeID":id,'host': '127.0.0.1', 'oper': 'election', 'message':{'ElectionStatus':'started' }}
            broad_caster.broadcast_message(message)
            #message = json.dumps(message)
            #message = str.encode(message)
            #broad_caster.send(message)
            # sedning again
            from bully_election import Election
            #broad_caster.broadcast_message(message)
            election = Election(id, groupView, leaderID, Leader, isElection, participation,lock,None)

            election.start()
            #election.join()
            return
    
    logger.info("^^^^^^^^^ Stopping Ping Service ^^^^^^^^^^^^^")
            
def broad_cast_health(id,Leader, broad_caster):
    
    """
    broadcast health if master
    1. start broadcasting health at interval of 1 second
    """
    logger.info("%%%%%%%%%%%%%%% starting broadcast health %%%%%%%%%%%%%%%%%%%%%")
    check = 1
    while check:
        #logger.info("Ping")
        message = {"id": id, "ping": True}
        #message = json.dumps(message)
        #message = str.encode(message)
        broad_caster.broadcast_message(message)
        time.sleep(0.1)
        check = Leader.value  # stop when there is no leader
    logger.info("Node:{},**********STOPPING HEALTH CHECK*************".format(id))    
    return