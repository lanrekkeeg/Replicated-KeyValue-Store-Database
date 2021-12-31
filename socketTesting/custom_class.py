from multiprocessing import Process, Manager
from multiprocessing.managers import BaseManager
from tinydb import TinyDB, Query
from tinydb import where
import os

class SimpleClass(object):
    def __init__(self):
        self.var = 0

    def set(self, value):
        self.var = value

    def get(self):
        return self.var


def change_obj_value(obj):
    print(obj.get())



class test(object):
    def __init__(self):
        self.data = self.load_all_buckets()

    def get(self):
        return self.data
        
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
    
    def drop_non_json(self,files):
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
        
    def get_bucket_name_in_db(self,path):
        """
        load all bucket names 
        """
        from os import walk
        filenames = next(walk(path), (None, None, []))[2]  # [] if no file
        return filenames
        
    def load_all_buckets(self):
        """
        loading all buckets
        """
        filenames = self.get_bucket_name_in_db("database")
        filenames = self.drop_non_json(filenames)
        bucket_object = self.creating_bucket_object(filenames)
        #bucket_object['registry'].add({"name":"test","new":123})
        print(bucket_object)
        return bucket_object
        
    def creating_bucket_object(self,filename):
        """
        load all bucket data in seperate objects
        """
        
        bucket_object = {}
        for bucket_name in filename:
            name_ = bucket_name.split('.')[0]
            bucket_object.update({name_:TinyDB("database/"+bucket_name)})
        return bucket_object
    
    def get_all_IDS(self,db_obj):
        """
        return all IDs in buckets
        """
        ids = [e.doc_id for e in db_obj.all()]
        return ids
    
    def update_by_id(self,db_obj,query):
        """
        update record base on ID
        """
        ids = self.get_all_IDS(db_obj)
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
    
    def update_by_query(self):
        """
        update record by query
        """
        
        pass
        
    def delete_by_id(self,db_obj, id_lst):
        """
        delete document by id
        """
        ids = self.get_all_IDS(db_obj)
        delted_id = []
        non_deleted_id = []
        for id in id_lst:
            if id in ids:
                self.db_obj.remove(doc_ids=[id])
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
                
    def search_by_id(self,db_obj, id):
        """
        """
        ids = self.get_all_IDS(db_obj)
        if id in ids:
            record = db_obj.get(doc_id=id)
            return record
        else:
            message = "No Record found with ID:"+str(id)
            return message
    
    def add_record(self,db_obj,data):
        """
        add record in bucket
        """
        id = self.db_obj.insert(data)
        return "Record added, ID is "+str(id)
        
    def search_by_query(self,db_obj, query):
        """
        """
        pass

if __name__ == '__main__':
    BaseManager.register('test', test)
    manager = BaseManager()
    manager.start()
    inst = manager.test()
    print ("___________________________\n",inst.get())    
    p = Process(target=change_obj_value, args=[inst])
    p.start()
    p.join()

    #print (inst)                    # <__main__.SimpleClass object at 0x10cf82350>
    print (inst.get())    