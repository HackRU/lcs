from pymongo import MongoClient
import validate
import config 
import random
import datetime
import string
from datetime import datetime, timedelta

def forgotUser(magiclink):
    magiclink = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
    obj_to_insert = {}
    obj_to_insert['email'] = event['email']
    obj_to_insert['link'] = magiclink
    obj_to_insert['forgot'] = True
    obj_to_insert[ "valid_until"] = (datetime.now() + timedelta(hours=3)).isoformat()
    magiclinks.insert_one(obj_to_insert)
    return magiclink

def directorLink(event):
        links_list = []
        for i in event['permissions']:
             permissions.append(i)
        for j in range(numLinks):
            magiclink = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
            obj_to_insert = {}
            obj_to_insert['permissions'] = permissions
            obj_to_insert['email'] = event['emailsTo'][j]
            obj_to_insert['forgot'] = False
            obj_to_insert['link'] = magiclink
            obj_to_insert["valid_until"] = (datetime.now() + timedelta(hours=3)).isoformat()
            links_list.append(magiclink)
            magiclinks.insert_one(obj_to_insert)
        return links_list

def genMagicLink(event,context):
    """
       The event object expects and email and  checks if it is a valid request to generate the magic link  
    """

    client = MongoClient(config.DB_URI)
    db = client['lcs-db']
    db.authenticate(config.DB_USER,config.DB_PASS)
    tests = db['test']
    magiclinks = db['magiclinks']
    if 'forgot' in event and 'email' in event:

        user = tests.find_one({"email":event['email']})
        if user:
            magiclink = forgotUser(magiclink)
            return config.add_cors_headers({"statusCode":200,"body":magiclink})
        else:
            return config.add_cors_headers({"statusCode":400,"body":"Invlaid email"})
        

    if 'email' not in event or 'token' not in event:

        return config.add_cors_headers({"statusCode":400,"body":"You forgot some params try a again"})
    #validate first
    ret_ = validate.validate(event,context);
    #if sucesfully validated 
    if(ret_['statusCode'] == 200):
        #defaul value of numlinks 1
        numLinks = 1
        if 'numLinks' not in event:
            numLinks = event['numLinks']
        permissions = []
        links_list = []
        user = tests.find_one({"email":event['email']})
        if user and user['role']['director'] and 'permissions' in event:
            #build permissions
            links_list = directorLink(event)
            return config.add_cors_headers({"statusCode":200,"body":str(links_list)})

        else:

                return config.add_cors_headers({"statusCode":400,"body":"Invalid permissions"})
    else:

        return config.add_cors_headers({"statusCode":400,"body":"Please input a proper auth token"})

def updateUserFromMagicLink(magiclink,event):
    """
        Updates User Based on a magic link
    """
    #if the user forgot, then read the password and change it
    if maglinkobj['forgot'] == True:
        pass_ = event['password']
        pass_ = hashlib.md5(pass_.encode('utf-8') ).hexdigest() 

def consumeUrl(event,context):
    """
        Lambda function to consume a url. Queries the database and checks permissions and updates accordingly
    """
    if 'link' not in event:
        return config.add_cors_headers({"statusCode":400,"body":"No magic link provided"})

    client = MongoClient(config.DB_URI)
    db = client['lcs-db']
    db.authenticate(config.DB_USER,config.DB_PASS)
    tests = db['test']
    magiclinks = db['magiclinks']
    maglinkobj = magiclinks.find_one({"link":event['link']}) 
    if maglinkobj:
        updateUserFromMagicLink(maglinkobj,event)



