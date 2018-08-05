import sys

sys.path.append("..")

import config
from pymongo import MongoClient

def connect_to_db():
    client = MongoClient(config.DB_URI)
    db = client['lcs-db']
    db.authenticate(config.DB_USER,config.DB_PASS)

    return db['test']

def dict_includes(dict1, dict2):
    return all(k in dict1 and dict2[k](dict1[k]) for k in dict2)

def expect_eq(value):
    if not hasattr(value, '__call__'):
        return lambda x: x == value
    return value

def expect_exist(v):
    return True

def http_dict(**kwargs):
    rv = {
        'headers': lambda h: dict_includes(h, {
            'Access-Control-Allow-Origin': expect_eq(('*',)),
            'Access-Control-Allow-Headers': expect_eq(('Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',)),
            'Access-Control-Allow-Credentials': expect_eq((True,))
        })
    }
    rv.update({k: expect_eq(kwargs[k]) for k in kwargs})
    return rv

def get_db_user(email):
    db = connect_to_db()
    return db.find_one({"email": email})
