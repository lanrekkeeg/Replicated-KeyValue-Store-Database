from tinydb import TinyDB, Query
from tinydb import where
import time
db = TinyDB("operations.json")
data = db.all()
''''
data.sort(key=lambda x:(time.mktime(time.strptime(x['send_time'], '%m/%d/%Y, %H:%M:%S')), x['message']['sqn_no']),reverse=True)
print(data)
data = data[:int(len(data)/2)] # take half
data.sort(key=lambda x:x['message']['sqn_no'],reverse=True)
print(data[0]['message'])

'''
ids = [e.doc_id for e in db.all()]
print(ids)
q = Query()

item = db.search(q.message.sqn_no > 1 and q.message.sqn_no < 4)
print(item)
