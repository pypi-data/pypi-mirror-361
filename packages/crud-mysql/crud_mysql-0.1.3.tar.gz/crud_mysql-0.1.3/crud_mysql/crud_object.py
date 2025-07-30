
import os
import json
from mysql_database import DatabaseCreds, Database
from .vars import DATABASE_HOST, DATABASE_PORT, DATABASE_USER, DATABASE_PASSWORD, DATABASE_NAME

class CrudObject:

    def __init__(self, object_type):
        try:
            crud = self.get_crud_object(object_type)
        except Exception as e: 
            raise(e)
        self.object_type = object_type
        self.allowd_methods = crud["allowd_methods"]
        self.fetch_all = crud["fetch_all"] == "true"

        schemas = self.get_schemas()
        db_creds = DatabaseCreds(DATABASE_HOST, DATABASE_USER, DATABASE_PASSWORD, DATABASE_PORT)
        self.db = Database(DATABASE_NAME, db_creds, schemas=schemas)

    def get_object(self, object_id):
        
        try: 
            object = self.db.get_object_by_id(self.object_type, object_id, as_dict=True)
        except:
            raise Exception(f"cant find {self.object_type} with id: {object_id}")
        return object

    def get_objects(self, filter, include_columns=[], exclude_columns=[]):
        
        object = self.db.get_filtered_list_of_objects(self.object_type, filter, include_columns, exclude_columns, as_dict=True)
        return object

    def create_object(self, object):
        
        id = self.db.add_object(self.object_type, object)
        return id

    def update_object(self, object_id , object):
        
        self.db.update_object(self.object_type, object_id, object)

    def delete_object(self, object_id):
        
        self.db.delete_object(self.object_type, object_id)

    def check_object_in_schema(self, object_type):
        is_valid = False
        databases = os.listdir('schemas')
        for database in databases:
            with open(os.path.join('schemas', database), 'r') as f:
                objects = json.loads(f.read())
                for object in objects:
                    if object_type == object:
                        is_valid = True
        return is_valid

    def get_crud(self):
        with open("crud.json", "r") as f:
            crud = json.loads(f.read())
        return crud
    
    def get_crud_object(self, path):
        crud = self.get_crud()
        if path not in crud:
            raise Exception('the path is not configured in crud.json')
        return crud[path]
    
    def get_schemas(self):
        schema = {}
        crud = self.get_crud()
        for obj in crud:
            schema[obj] = crud[obj]["schema"]
        return schema