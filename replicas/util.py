import time

def sort_dict(data):
    """
    sort dictionary data
    """
    data.sort(key=lambda x:(time.mktime(time.strptime(x['send_time'], '%m/%d/%Y, %H:%M:%S')), x['message']['sqn_no']),reverse=True)
    return data

    