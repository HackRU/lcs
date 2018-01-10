import string
import json
import pymongo
from pymongo import MongoClient
import config
import hashlib

# context param for should include info of account the method is accessed from 

def read_info(event, context):
    # queries based on email, role and password - leave as empty string if not specified
    email = event['email']
    role = event['role']
    if email == '' and role == '':
        return {"statusCode":200, body:"no data to query on"}

    client = MongoClient(config.DB_URI)

    db = client['camelot-test']
    db.authenticate(config.DB_USER, config.DB_PASS)

    tests = db['test']

    if context['role'] == 'director' or context['role'] == 'organizer':
        query = {} 
        
        if email != '':
            query['email'] = email

        if role != '':
            query['role'] = role

        query = json.dumps(query)
    
        pipeline = [{"$match": query}]

        return db.command('aggregate', 'test', pipeline = pipeline, explain = True) # explain set to true for testing 

    else:
        data = tests.find_one({"email":context['email']})
        return ({"email":data['email'], "role":data['role']}) 

