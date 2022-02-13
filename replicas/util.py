import time

def sort_dict(data):
    """
    sort dictionary data
    """
    data.sort(key=lambda x:(time.mktime(time.strptime(x['send_time'], '%m/%d/%Y, %H:%M:%S')), x['message']['sqn_no']),reverse=True)
    return data

def encode_message(message):
    """
    encode message into byte like string
    """
    message = json.dumps(message)
    message = str.encode(message)
    return message
    

def check_multicast(message):
    """
    """
    if message.get("multicast", None) is not None:
        return True
    else:
        return False

def ignore_replica(message):
    """
    """
    if message.get("replica_message",None) is not None:
        return True
    
    else:
        return False
        
def ignore_cordinatro(message):
    """
    """
    
    if message.get("internal",None) is not None:
        return True
    else:
        return False