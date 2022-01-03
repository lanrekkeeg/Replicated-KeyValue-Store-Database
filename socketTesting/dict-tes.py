from tinydb import TinyDB, Query
from tinydb import where

db = TinyDB("operations.json")
ids = [e.doc_id for e in db.all()]
print(ids)
q = Query()

item = db.search(q.message.sqn_no > 0)
print(item)