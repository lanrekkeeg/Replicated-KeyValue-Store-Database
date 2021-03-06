import logging
from conf import *
import socket
import json

class MulticastSend(object):
    def __init__(self, id):
        self.MCAST_GRP = MCAST_GRP
        self.MCAST_PORT = MCAST_PORT
        self.id = id
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32)
        
    def broadcast_message(self, message):
        """
        convert into byte format and multicast message to group
        """
        message = json.dumps(message)
        message = str.encode(message)
        #self.broad_cast_sender.settimeout(0.2)
        #logger.debug("Broadcasting message ...")
        self.sock.sendto(message, (self.MCAST_GRP, self.MCAST_PORT))
        
class MulticastRec(object):
    def __init__(self, id):
        self.MCAST_GRP = MCAST_GRP
        self.MCAST_PORT = MCAST_PORT
        self.id = id    
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        try:
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except AttributeError:
            pass
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32) 
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
  
        self.sock.bind((self.MCAST_GRP, self.MCAST_PORT))
        host = socket.gethostbyname(socket.gethostname())
        self.sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(host))
        self.sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, 
                     socket.inet_aton(self.MCAST_GRP) + socket.inet_aton(host))

