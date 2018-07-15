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
    for k in dict2:
        if k not in dict1 or not dict2[k](dict1[k]):
            return False
    return True

def expect_eq(value):
    if not hasattr(value, '__call__'):
        return lambda x: x == value
    else:
        return value

def expect_exist(v):
    return True

def http_dict(**kwargs):
    rv = {
        'headers': lambda h: dict_includes(h, {
            'Access-Control-Allow-Origin': expect_eq('*'),
            'Access-Control-Allow-Headers': expect_eq('Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'),
            'Access-Control-Allow-Credentials': expect_eq(True)
        })
    }
    rv.update({k: expect_eq(kwargs[k]) for k in kwargs})
    return rv
