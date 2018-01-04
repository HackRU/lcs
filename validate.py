import string
import json
import pymongo
from pymongo import MongoClient
import config
import requests

def validate(event, context):
    
    if 'email' not in event or 'authtokens' not in event:
        return ({"statusCode":400, "body":"Data not submitted."})

    email = event['email']
    token = event['authtoken']

    client = MongoClient(config.DB_URI)
    db = client['camelot-test']
    db.authenticate(config.DB_USER, config.DB_PASS)
    
    tests = db['test']

    results = tests.find_one({"email":email})

    if results == None or results == [] or results == ():
        return ({"statusCode":400,body:"Email not found."})

    if token not in results['authtokens']:
        return ({"statusCode":400,body:"Authentication token is invalid."})

    return ({"statusCode":200,"body":"Successful request."})


def validate_qr(event, context):

    if 'user_email' not in event or 'authtoken' not in event:
        return ({"statusCode":400, "body":"Data not submitted."})

    u_email = event['user_email']
    token = event['authtoken']

    client = MongoClient(config.DB_URI)
    db = client['camelot-test']
    db.authenticate(config.DB_USER, config.DB_PASS)
    
    tests = db['test']

    results = tests.find_one({"email":u_email})

    if results == None or results == [] or results == {}:
        return ({"statusCode":400,"body":"User email not found."})

    if token not in results['authtokens']:
        return ({"statusCode":400, "body":"Authentication token not found."})

    return ({"statusCode":200, "body":"Successful request."})

