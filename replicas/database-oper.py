from tinydb import TinyDB, Query
from tinydb import where
import os

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
    
def load_all_buckets():
    """
    loading all buckets
    """
    filenames = get_bucket_name_in_db("database")
    filenames = drop_non_json(filenames)
    bucket_object = creating_bucket_object(filenames)
    #bucket_object['registry'].add({"name":"test","new":123})
    print(bucket_object)

def creating_bucket_object(filename):
    """
    load all bucket data in seperate objects
    """
    
    bucket_object = {}
    for bucket_name in filename:
        name_ = bucket_name.split('.')[0]
        bucket_object.update({name_:TinyDB("database/"+bucket_name)})
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
    ids = get_all_IDS()
    if id in query["id"]:
        try:
            record = db_obj.update(query['query'],doc_id=id)
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
    
def delete_by_id(db_obj, id):
    """
    delete document by id
    """
    ids = get_all_IDS(db_obj)
    if id in ids:
        db_obj.remove(doc_ids=id)
        message = "Record with ID:"+str(id)+" is deleted..."
        return message
    else:
        message = "No Record found with ID:"+str(id)
        return message
    
def search_by_id(db_obj, id):
    """
    """
    ids = get_all_IDS()
    if id in ids:
        record = db_obj.get(doc_id=id)
        return record
    else:
        message = "No Record found with ID:"+str(id)
        return message
        
def search_by_query(db_obj, query):
    """
    """
    pass

load_all_buckets()