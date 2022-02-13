 
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
try:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
except AttributeError:
    pass
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32) 
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
import platform
        # otherwise very difficult to run one copy in windows and other in macbook
#if platform.system == 'Windows':
sock.bind(("",34024))
#else:
#    sock.bind(MCAST_GRP,MCAST_PORT)