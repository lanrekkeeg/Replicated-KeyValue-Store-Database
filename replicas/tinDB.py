from tinydb import TinyDB, Query
from tinydb import where

from tinydb.operations import delete, increment, decrement, add, subtract, set

db = TinyDB('database/db.json')
#User = Query()
#print(db.search(User.int == 1))
id = db.insert({'int': 1})
print("record id is ",id)
#print(db.remove(doc_ids=[7]))
ids = [e.doc_id for e in db.all()]
print(ids)
db.update({"new":12,"int":4}, doc_ids=[ids[0]])
print("record is ", db.get(doc_id=ids[0]))

#db.update(delete('int'), where('char') == 'a')
User = Query()
print(db.search(User.nothing == 1))