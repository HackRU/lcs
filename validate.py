import string
import json
import pymongo
from pymongo import MongoClient
import config
import requests
import dateutil.parser as dp
import datetime

def validate(event, context):
    if 'email' not in event or 'token' not in event:
        return config.add_cors_headers({"statusCode":400, "body":"Data not submitted."})

    email = event['email']
    token = event['token']

    client = MongoClient(config.DB_URI)
    db = client['camelot-test']
    db.authenticate(config.DB_USER, config.DB_PASS)

    tests = db['test']

    results = tests.find_one({"email":email})

    if results == None or results == [] or results == ():
        return config.add_cors_headers({"statusCode":400,body:"Email not found."})

    if not any(i['auth']['token'] == token and datetime.now() < dp.parse(i['auth']['valid_until']) for i in results['authtokens']):
        return config.add_cors_headers({"statusCode":400,body:"Authentication token is invalid."})

    return config.add_cors_headers({"statusCode":200,"body":"Successful request."})


def update(event, context):
    if 'user_email' not in event or 'authtoken' not in event or 'auth_email' not in event:
        return config.add_cors_headers({"statusCode":400, "body":"Data not submitted."})

    u_email = event['user_email']
    a_email = event['auth_email']
    auth_val =  event['auth']

    client = MongoClient(config.DB_URI)
    db = client['camelot-test']
    db.authenticate(config.DB_USER, config.DB_PASS)

    tests = db['test']

    results = tests.find_one({"email":u_email})

    if results == None or results == [] or results == {}:
        return config.add_cors_headers({"statusCode":400,"body":"User email not found."})

    a_res = tests.find_one({"email": a_email})

    if a_res == None or a_res == [] or a_res == {}:
        return config.add_cors_headers({"statusCode":400,"body":"Auth email not found."})

    if token not in a_res['auth']['token']:
        return config.add_cors_headers({"statusCode":400, "body":"Authentication token not found."})

    return config.add_cors_headers({"statusCode":200, "body":"Successful request."})

