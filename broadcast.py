import socket
import time
class Broadcaster:
    def __init__():
        broad_cast_receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) # UDP
        broad_cast_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        broad_cast_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        broad_cast_sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        # Enable broadcasting mode
        broad_cast_sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        broad_cast_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        broad_cast_receiver.bind(("", 37020))
        
        
    def listen_to_broadcast_message(self):
        while True:
            # Thanks @seym45 for a fix
            data, addr = self.broad_cast_receiver.recvfrom(1024)
            
            # perform operation base on this data
            print("received message: %s"%data)
        
    
    # we will pass message we want to broadcast
    def broad_cast_message(self):
        self.broad_cast_sender.settimeout(0.2)
        message = b"your very important message"
        while True:
            self.broad_cast_sender.sendto(message, ('<broadcast>', 37020))
            print("message sent!")
            time.sleep(1)
                
        
