import string
import random
import json
import pymongo
from pymongo import MongoClient
import config
import requests

def gen (size = 20, chars = string.ascii_lowercase + string.digits + string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))

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

    dat = tests.find_one({"email":event['email'], "password":event['password']})
    if dat == None or dat == [] or dat == ():
        return ({"statusCode":403,"body":"invalid email,hash combo"})
    #check if the hash is correct
    checkhash  = tests.find_one({"email":event['email']})
    if(checkhash['password'] != event['password']):
        return ({"statusCode":403,"Body":"Wrong Password"})
    token = gen()
    bod_ = {"authtoken":token}
    tests.update({"email":event['email']},{"$push":{"authtokens":token}})
    #append to list of auth tokens
    ret_val = { "statusCode":200,"isBase64Encoded": False, "headers": { "Content-Type":"application/json" },"body" :json.dumps(bod_)}
    return ret_val

def create_user(event, context):
    pass

def mlh_callback(event, context):
    params = config.MLH.copy()
    params['code'] = event['queryStringParameters']['code']
    access_tok_json = requests.post(MLH_TOK_BASE_URL, params=params).json()
    access_token = access_tok_json[u'access_token']
    scopes = access_tok_json[u'scope']

    mlh_user = requests.get(MLH_TOK_BASE_URL, params={'access_token': access_token}).json()

    if mlh_user[u'status'] != 'OK':
        return ({"statusCode":400,"body":"MLH Troubles!"})

    client = MongoClient(config.DB_URI)
    db = client['camelot-test']
    db.authenticate(config.DB_USER,config.DB_PASS)
    tests = db['test']
    user = test.find_one({'email': mlh_user[u'data'][u'email']})
    if user == None or user == [] or user == ():
        #making new user here
        event['user_data'] = mlh_user['data']
        return create_user(event, context)
    else:
        #auth
        event['email'] = user['email']
        event['password'] = user['password']
        #Kosher?
        return authorize(event, context)
