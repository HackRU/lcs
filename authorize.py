import string
import random
import json
import pymongo
from pymongo import MongoClient
import config
import requests
import hashlib
from datetime import datetime, timedelta
import uuid

MLH_TOK_BASE_URL = 'https://my.mlh.io/oauth/token'
MLH_USER_BASE_URL = 'https://my.mlh.io/api/v2/user.json'

def authorize(event,context):
    if('email' not in event  or 'password' not in event):
        return ({"statusCode":400,"body":"Invalid Request"})
    
    email = event['email']
    pass_ = event['password']
    client = MongoClient(config.DB_URI)
    
    db = client['camelot-test']
    db.authenticate(config.DB_USER,config.DB_PASS)
    
    tests = db['test']

    dat = tests.find_one({"email":event['email'], "hash_password":event['password']})
    if dat == None or dat == [] or dat == ():
        return ({"statusCode":403,"body":"invalid email,hash combo"})
    
    #check if the hash is correct
    checkhash  = tests.find_one({"email":event['email']})
    
    if(checkhash['hash_password'] != event['password']):
        return ({"statusCode":403,"Body":"Wrong Password"})
    
    token = str(uuid.uuid4())
    
    bod_ = {"authtoken":token}
    
    update_val = 
    {"auth":
        {
            "token":token,
            "valid_until":(datetime.datetime.now() + timedelta(hours=3)).isoformat()
        }
    }

    tests.update({"email":event['email']},{"$push":update_val})
    
    #append to list of auth tokens
    ret_val = { "statusCode":200,"isBase64Encoded": False, "headers": { "Content-Type":"application/json" },"body" :json.dumps(bod_)}
    return ret_val

def mlh_callback(event, context):
    params = config.MLH.copy()
    if 'code' not in event['queryStringParameters']:
        access_token = event['queryStringParameters'].get('access_token')
        if access_token is None:
            return ({"statusCode":400,"body":"MLH Troubles! No access token."})
    else:
        params['code'] = event['queryStringParameters']['code']
        access_tok_json = requests.post(MLH_TOK_BASE_URL, params=params).json()
        access_token = access_tok_json['access_token']
        scopes = access_tok_json['scope']

    mlh_user = requests.get(MLH_USER_BASE_URL, params={'access_token': access_token}).json()

    if mlh_user['status'] != 'OK':
        return ({"statusCode":400,"body":"MLH Troubles!"})

    client = MongoClient(config.DB_URI)
    db = client['camelot-test']
    db.authenticate(config.DB_USER,config.DB_PASS)
    test = db['test']
    user = test.find_one({'email': mlh_user['data']['email']})
    if user == None or user == [] or user == ():
        #making new user here
        mlh_user['data']['role'] = 'hacker'
        mlh_user['data']['sp_pass'] = 'fudging Hari'
        return create_user(mlh_user['data'], context)
    else:
        #auth
        event['email'] = user['email']
        event['password'] = user['password']
        #Kosher?
        return authorize(event, context)


def create_user(event, context):
        
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
                                                                                     
    doc = { "email": u_email, 
            "role": role, 
            "sp_password": hashlib.md5(sp_pass.encode('utf-8')).hexdigest(), 
            "password": hashlib.md5(password.encode('utf-8')).hexdigest()
          }

    tests.insert(doc)

    return authorize(event, context)

