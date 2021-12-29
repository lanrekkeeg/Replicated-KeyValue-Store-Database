# Echo client program
import socket
import time
import json
HOST = '127.0.0.1'    # The remote host
PORT = 50007              # The same port as used by the server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
message = {'host': '127.0.0.1', 'port':'Null', 'channel': 'election', 'message':{'ElectionIniated':1, 'From':1}}
msg_dump = json.dumps(message)

s.connect((HOST, PORT))
s.send(str.encode(msg_dump))
data = s.recv(1024)
#s.close()
data =  data.decode()
data = json.loads(data)
print ('Received', data['message'])
s.send(b"seems like connection is working..")
s.settimeout(0.00001)

try:
    data = s.recv(1024)
except socket.timeout as e:
    print(e)
#s.close()
print ('Received', repr(data))
time.sleep(60)