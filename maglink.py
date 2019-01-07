from pymongo import MongoClient
import validate
import config
import random
import datetime
import string
import use_sparkpost
from datetime import datetime, timedelta

def forgotUser(event,magiclinks):
    magiclink = 'forgot-' +  ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
    obj_to_insert = {}
    obj_to_insert['email'] = event['email']
    obj_to_insert['link'] = magiclink
    obj_to_insert['forgot'] = True
    obj_to_insert[ "valid_until"] = (datetime.now() + timedelta(hours=3)).isoformat()
    magiclinks.insert_one(obj_to_insert)
    link_base = event.get('link_base', 'https://hackru.org/magic/{}')
    rv = use_sparkpost.send_email(event['email'], link_base.format(magiclink),True)
    if rv['statusCode'] != 200:
        return rv
    return magiclink

def directorLink(magiclinks, numLinks, event):
        links_list = []
        permissions = []
        for i in event['permissions']:
             permissions.append(i)
        for j in range(min(numLinks, len(event['emailsTo']))):
            magiclink = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
            obj_to_insert = {}
            obj_to_insert['permissions'] = permissions
            obj_to_insert['email'] = event['emailsTo'][j]
            obj_to_insert['forgot'] = False
            obj_to_insert['link'] = magiclink
            obj_to_insert["valid_until"] = (datetime.now() + timedelta(hours=3)).isoformat()
            magiclinks.insert_one(obj_to_insert)
            sent = use_sparkpost.send_email(obj_to_insert['email'],magiclink,False)['body']
            links_list.append((magiclink, sent))
        return links_list

def genMagicLink(event,context):
    """
       The event object expects and email and  checks if it is a valid request to generate the magic link  
    """

    client = MongoClient(config.DB_URI)
    db = client[config.DB_NAME]
    db.authenticate(config.DB_USER,config.DB_PASS)
    tests = db[config.DB_COLLECTIONS['users']]
    magiclinks = db[config.DB_COLLECTIONS['magic links']]
    if 'forgot' in event and 'email' in event:
        user = tests.find_one({"email":event['email']})
        if user:
            magiclink = forgotUser(event,magiclinks)
            return config.add_cors_headers({"statusCode":200,"body":"Forgot password link has been emailed to you"})
        else:
            return config.add_cors_headers({"statusCode":400,"body":"Invalid email: please create an account."})

    if 'email' not in event or 'token' not in event or 'permissions' not in event or 'emailsTo' not in event:
        return config.add_cors_headers({"statusCode":400,"body":"You forgot some params try again"})
    #validate first
    ret, user = validate.get_validated_user(event);
    #if sucesfully validated
    if ret:
        #default value of numlinks 1
        numLinks = 1
        if 'numLinks' in event:
            numLinks = event['numLinks']
        permissions = []
        links_list = []
        user = tests.find_one({"email":event['email']})
        if user and user['role']['director']:
            #build permissions
            links_list = directorLink(magiclinks, numLinks,event)
            return config.add_cors_headers({"statusCode":200,"body":links_list})
        else:
            return config.add_cors_headers({"statusCode":400,"body":"Invalid permissions"})
    else:
        return config.add_cors_headers({"statusCode":400,"body":user})

