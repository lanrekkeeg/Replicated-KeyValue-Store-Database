import socket

def send(data, port=50000, addr='239.192.1.100'):
        """send(data[, port[, addr]]) - multicasts a UDP datagram."""
        # Create the socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Make the socket multicast-aware, and set TTL.
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 20) # Change TTL (=20) to suit
        # Send the data
        data = b"hello world"
        while True:
                s.sendto(data, (addr, port))

send("heel")