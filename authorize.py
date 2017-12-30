import string
import random
import json
import pymongo
from pymongo import MongoClient
import config
print(pymongo.version)
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
    #querydb 
    
    #generate auth token
    token = gen()
    bod_ = {"authtoken":token}
    ret_val = { "statusCode":200,"isBase64Encoded": False, "headers": { "Content-Type":"application/json" },"body" :json.dumps(bod_)}
    return ret_val
def gen (size = 20, chars = string.ascii_lowercase + string.digits + string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))


