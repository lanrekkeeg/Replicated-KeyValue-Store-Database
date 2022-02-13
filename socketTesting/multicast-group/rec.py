import socket
MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007
id = id    
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

try:
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
except AttributeError:
    pass
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 32) 
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)
  
  
host = socket.gethostbyname(socket.gethostname())
print(host," is")
sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_IF, socket.inet_aton(host))
sock.setsockopt(socket.SOL_IP, socket.IP_ADD_MEMBERSHIP, 
                     socket.inet_aton(MCAST_GRP) + socket.inet_aton(host))
import platform
        # otherwise very difficult to run one copy in windows and other in macbook
if platform.system() == 'Windows':
    sock.bind(('', MCAST_PORT))
else:
    sock.bind((MCAST_GRP,MCAST_PORT))
    
    
while True:
    data, addr = sock.recvfrom(1024)
    print("incoming data is:{}".format(data))