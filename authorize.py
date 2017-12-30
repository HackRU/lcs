import string
import random
import json
from pymongo import MongoClient
import config
def authorize(event,context):

    if('email' not in event  or 'password' not in event):
        return ({"statusCode":400,"body":"Invalid Request"})
    email = event['email']
    pass_ = event['password']
    client = MongoClient(config.DB_URI)
     
    #querydb 
    
    #generate auth token
    token = gen()
    bod_ = {"authtoken":token}
    ret_val = { "statusCode":200,"isBase64Encoded": False, "headers": { "Content-Type":"application/json" },"body" :json.dumps(bod_)}
    return ret_val
def gen (size = 20, chars = string.ascii_lowercase + string.digits + string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))

