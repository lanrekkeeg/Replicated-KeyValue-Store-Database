from tinydb import TinyDB, Query
from tinydb import where
import os

global db_buckets
global db_operation

def process_query(request):
    """
    it will process the requery
    """
    opera = request['oper']
    
    if opera == "create":
        """
        Create bucket in database
        """
        pass

def drop_non_json(files):
    """
    drop non-json file 
    """
    new_file_list = []
    for f in files:
        if "json" in f.split("."):
            new_file_list.append(f)
        else:
            print("dropping unimportant files")
    return new_file_list
    
def get_bucket_name_in_db(path):
    """
    load all bucket names 
    """
    from os import walk
    filenames = next(walk(path), (None, None, []))[2]  # [] if no file
    return filenames
    
def load_all_buckets(path):
    """
    loading all buckets
    """
    filenames = get_bucket_name_in_db(path)
    filenames = drop_non_json(filenames)
    bucket_object = creating_bucket_object(filenames, path)
    #bucket_object['registry'].add({"name":"test","new":123})
    #print(bucket_object)
    return bucket_object

    
    
def creating_bucket_object(filename, path):
    """
    load all bucket data in seperate objects
    """
    
    bucket_object = {}
    for bucket_name in filename:
        name_ = bucket_name.split('.')[0]
        bucket_object.update({name_:TinyDB(path+bucket_name)})
    return bucket_object

def get_all_IDS(db_obj):
    """
    return all IDs in buckets
    """
    ids = [e.doc_id for e in db_obj.all()]
    return ids

def update_by_id(db_obj,query):
    """
    update record base on ID
    """
    ids = get_all_IDS(db_obj)
    if query["id"] in ids:
        try:
            record = db_obj.update(query['query'],doc_ids=[query["id"]])
            return "Record updated sucessfully"
        except Exception as exp:
            return "Failed to update record, error is "+str(exp)
    else:
        message = "No Record found with ID:"+str(id)
        return message
    
    pass

def update_by_query():
    """
    update record by query
    """
    
    pass
    
def delete_by_id(db_obj, id_lst):
    """
    delete document by id
    """
    ids = get_all_IDS(db_obj)
    delted_id = []
    non_deleted_id = []
    for id in id_lst:
        if id in ids:
            db_obj.remove(doc_ids=[id])
            #message = "Record with ID:"+str(id)+" is deleted..."
            #return message
            delted_id.append(id)
        else:
            non_deleted_id.append(id)
    
    if len(non_deleted_id) !=0 and len(delted_id) == 0:
        message =  "No Record found with ID:"+str(id_lst)
        # all record deleted
    elif len(non_deleted_id) ==0 and len(delted_id) !=0:
        #message = "Record with ID:"+str(delted_id)+" is deleted..."
        message = "Record with ID:"+str(delted_id)+" is deleted"
        # half deleted and half not deleted
    elif len(non_deleted_id) != 0 and len(delted_id) !=0:
        message = "Record with ID:"+str(delted_id)+" is deleted and No Record found with ID:"+str(non_deleted_id)
    
    return message
            
def search_by_id(db_obj, id):
    """
    """
    ids = get_all_IDS(db_obj)
    if id in ids:
        record = db_obj.get(doc_id=id)
        return record
    else:
        message = "No Record found with ID:"+str(id)
        return message

def add_record(db_obj,data):
    """
    add record in bucket
    """
    id = db_obj.insert(data)
    return "Record added, ID is "+str(id)


# for fault tolerance and recovery
def get_marker_records(db_obj, sqn_no):
    """
    receive markar and return all records
    """
    q = Query()
    history = db_obj.search(q.message.sqn_no > sqn_no)
    return history
    
def search_by_query(db_obj, query):
    """
    """
    pass
    
def get_last_save_sqn_no():
    """
    return last store sqn number
    """
# Testing 
db_buckets = load_all_buckets("database/")
db_operation = load_all_buckets("database_oper_log/")
cordinator_logs = load_all_buckets("cordinator_logs/")
#bck = load_all_buckets()
#qry = {"id":9,"query":{"status":"updated"}}
#print(search_by_id(bck['db'],3))
#print(delete_by_id(bck['db'],[3,20,34,45]))
#print(update_by_id(bck['db'],qry))
#print(add_record(bck['db'],{"test":1244}))