import string
import json
import pymongo
from pymongo import MongoClient
import config
import requests
from email_validator import validate_email, EmailNotValidError
import hashlib

def create(event, context):
    
    # check if valid email
    try:
       email = validate_email(event['email'])
    except EmailNotValidError as e:
        return ({"statusCode":400, "body":e})

    u_email = event['email']
    role = event['role']
    sp_pass = event['sp_pass']
    password = event['password']

    if role != 'hacker' and sp_pass == '':
        return ({"statusCode":400, "body":"Special password needed."})

    client = MongoClient(config.DB_URI)
    db = client['camelot-test']
    db.authenticate(config.DB_USER, config.DB_PASS)

    tests = db['test']
    
    doc = {
            "email": u_email,
            "role": role, 
            "sp_password": hashlib.md5(sp_pass.encode('utf-8')).hexdigest(),
            "hash_password": hashlib.md5(password.encode('utf-8')).hexdigest()
    }

    tests.insert(doc)

    return ({"statusCode":200, "body":"Successful request."})

