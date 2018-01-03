import string
import json
import pymongo
from pymongo import MongoClient
import config
import requests

def validate(event, context):
    
    if 'authtokens' not in event:
        return false
    
    f_name = event['first_name']
    l_name = event['last_name']
    token = event['authtokens']

    client = MongoClient(config.DB_URI)
    db = client['camelot-test']
    db.authenticate(config.DB_USER, config.DB_PASS)
    
    tests = db['test']

    results = tests.find_one({"authtokens":token})

    if results == None or results == [] or results == ():
        return false

    return results['first_name'] == f_name and results['last_name'] == l_name

def validate_qr(event, context):

    email_address = event['email']
    token = event['authtokens']

    client = MongoClient(config.DB_URI)
    db = client['camelot-test']
    db.authenticate(config.DB_USER, config.DB_PASS)
    
    tests = db['test']

    results = tests.find_one({"authtokens":token})
    
    if results == None or results == [] or results == ():
        return false

    return email_address == results['email']

