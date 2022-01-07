
from logging import Logger
import socket
import json
import time
import uuid
import datetime
class KeyStore(object):
    
    def __init__(self):
        """"
        """
        self.cord_ip = None
        self.cord_port = None
        self.broad_ip = "192.168.0.255"
        self.broad_port = 37020
        self.client_id = str(uuid.uuid4())
        self.establish_connection()
        
    
    def establish_connection(self):
        """
        """
        
        self.cord_ip, self.cord_port = self.acquire_cordinator()
        self.client_conn = self.get_tcp_sock()
        self.client_conn.connect((self.cord_ip, self.cord_port))
        
    def check_param(self,bucket_name= ".", id= ".", body= "."):
        """
        check param
        """
        print(bucket_name, id, body)
        if bucket_name == None:
            raise Exception("Bucket name param is missing")
        if id == None:
            raise Exception("id param is missing")
        if body == None:
            raise Exception("body param is missing")
    
    def send_data(self, message):
        """
        sending data to client
        """
        message = json.dumps(message)
        message = str.encode(message)
        try:
            self.client_conn.send(message)
        except Exception as exp:
            print("Got error,{}".format(exp))
            self.establish_connection()
            # recursion for continous connection, eventually will break
            self.send_data(message)
            
        
    def recv_data(self):
        """
        """
        try:
            data = self.client_conn.recv(1024)
            return data
        except socket.error:
            print("Connection break with cordinator, Establishing connection...")
            self.establish_connection()
        return None
            #raise Exception("Error while reading write response..")
            
    def create_db_connection(self):
        """
        """
        pass
    def decode_data(self,message):
        """
        """
        message = message.decode()
        message = json.loads(message)
        return message
        
    def write(self, bucket_name=None, body=None):
        """
        """
        self.check_param(bucket_name,body)
        message = {"nodeID":self.client_id,"oper": "key-value", "message":{"oper-type": "write", "bucket_name":bucket_name,"content":body}}
        self.send_data(message)
        #print("Writing data to DB successfulyy")
        data = self.recv_data()
        if data:
            data = self.decode_data(data)
            return data
        return data
    
    def readbyID(self, bucket_name=None, id=None):
        """
        """
        self.check_param(bucket_name, id)
        message = {"nodeID":self.client_id,"oper": "key-value", "message":{"oper-type": "searchbyID", "bucket_name":bucket_name,"content":{"id":id}}}
        self.send_data(message)
        data = self.recv_data()
        if data:
            data = self.decode_data(data)
            return data
        return data
        
    
    def deletebyID(self, bucket_name=None, id=None):
        """
        """
        self.check_param(bucket_name, id)
        message = {"nodeID":self.client_id,"oper": "key-value", "message":{"oper-type": "deletebyID", "bucket_name":bucket_name,"content":{"id":id}}}
        self.send_data(message)
        data = self.recv_data()
        if data:
            data = self.decode_data(data)
            return data
        return data
        pass
    
    def updatebyID(self, bucket_name, data, id):
        """
        """
        pass
        
    def send_ping_to_cordinator(self, broad_cast_sender):
        """
        """
        message = {"nodeID":self.client_id,"oper": "status", "message":{"status": "leader","from":"client"}}
        self.broad_cast_message(message,broad_cast_sender)
        
    def acquire_cordinator(self):
        """
        """
        print("Checking for leader IP")
        broad = self.get_broad_cast_send_socket()
        self.send_ping_to_cordinator(broad)
        broad_cast_receiver = self.get_broad_cast_recv_socket()
        ts_old = datetime.datetime.now()
        ts_new = datetime.datetime.now()
        while (ts_new-ts_old).total_seconds()<=10:
            try:
                data, addr = broad_cast_receiver.recvfrom(1024)
            
            except Exception as exp:
                print("Error in receving multicat")
                raise Exception("Cordinator is down, Please Try again later")

            message = data.decode()
            message = json.loads(message)
            if message.get("oper",None) == "response":
                print(message)
    
                if message['message'].get('leader', None) is not None:
                    print("Leader data is {}".format(message['message']))
                    if self.test_cordinator_connection(message['message']['host'], int(message['message']['port'])):
                        print("Returning leader ip to client")
                        return message['message']['host'],message['message']['port']
            
            ts_new = datetime.datetime.now()
            broad.close()
            broad_cast_receiver.close()
            broad_cast_receiver = self.get_broad_cast_recv_socket()
            broad = self.get_broad_cast_send_socket()
            self.send_ping_to_cordinator(broad)
        raise Exception("Cordinator is down, Please Try again later")
            
    def get_tcp_sock(self):
        """
        """
        client  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        client.settimeout(7)
        return client
        
    def test_cordinator_connection(self, ip, port):
        """
        """
        try:
            client  = self.get_tcp_sock()
            client.connect((ip, port))
            message = {"acquire":"master"}
            message = json.dumps(message)
            message = str.encode(message)
            client.send(message)
            
            data = client.recv(1024)
            data = data.decode()
            data = json.loads(data)
            if data.get("isLeader",None) == 1:
                client.close()
                print("Test passed")
                return 1
            else:
                client.close()
                print("Test failed")
                return 0
        except socket.error as exp:
            print("Error in testing connection, {}".format(exp))
            client.close()
            return 0
        return 1
        
    def broad_cast_message(self, message, broad_cast_sender):
        """
        """
        message = json.dumps(message)
        message = str.encode(message)    
        broad_cast_sender.sendto(message,(self.broad_ip, self.broad_port))
        
    def get_broad_cast_send_socket(self):
        """
        """
        broad_cast_sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        broad_cast_sender.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        broad_cast_sender.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        return broad_cast_sender
        
    def get_broad_cast_recv_socket(self):
        """
        """
        
        broad_cast_receiver = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) 
        broad_cast_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        broad_cast_receiver.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        broad_cast_receiver.settimeout(10)
        broad_cast_receiver.bind((self.broad_ip, self.broad_port))
        
        return broad_cast_receiver
        