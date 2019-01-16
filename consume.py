from pymongo import MongoClient
from schemas import *
import config

import string
from datetime import datetime, timedelta
import bcrypt

@ensure_schema({
    "type": "object",
    "properties": {
        "email": {"type": "string", "format": "email"},
        "token": {"type": "string"}
    },
    "required": ["email", "token"]
})
@ensure_logged_in_user()
def promotion_link(event, maglinkobj, user, userCollection):
    """
        Updates User Based on a magic link
    """
    #Grab the permissions object
    permissions = maglinkobj['permissions']
    for i in permissions:
        if i == 'director':
            userCollection.update_one({'email':user['email']}, {'$set':{'role.director':True}})
        elif i == 'judge':
            userCollection.update_one({'email':user['email']}, {'$set':{'role.judge':True}})
        elif i == 'organizer':
            userCollection.update_one({'email':user['email']}, {'$set':{'role.organizer':True}})
        elif i == 'volunteer':
            userCollection.update_one({'email':user['email']}, {'$set':{'role.volunteer':True}})
        elif i == 'mentor':
            userCollection.update_one({'email':user['email']}, {'$set':{'role.mentor':True}})

    return {"statusCode":200, "body":"Successfully updated your role"}

@ensure_schema({
    "type": "object",
    "properties": {
        "password": {"type": "string"},
    },
    "required": ["password"]
})
def forgot_password_link(event, userCollection, maglinkobj):
    pass_ = event['password']
    pass_ = bcrypt.hashpw(pass_.encode('utf-8'), bcrypt.gensalt(rounds=8))
    checkifmlh = userCollection.find_one({"email":maglinkobj['email']})
    if not checkifmlh:
        return {
            "statusCode": 400,
            "body": "We could not find that email."
        }

    userCollection.update_one({"email":maglinkobj['email']},{'$set':{'password':pass_}})
    return {"statusCode":200,"body":"Sucessfully updated your password"}

@ensure_schema({
    "type": "object",
    "properties": {
        "link": {"type": "string"},
    },
    "required": ["link"]
})
def consumeUrl(event,context):
    """
        Lambda function to consume a url. Queries the database and checks permissions and updates accordingly
    """
    client = MongoClient(config.DB_URI)
    db = client[config.DB_NAME]
    db.authenticate(config.DB_USER,config.DB_PASS)
    #user collection
    tests = db[config.DB_COLLECTIONS['users']]
    #maglink collection
    magiclinks = db[config.DB_COLLECTIONS['magic links']]
    maglinkobj = magiclinks.find_one({"link":event['link']})
    if maglinkobj:
        if maglinkobj['forgot']:
            statusCode = forgot_password_link(event, tests, maglinkobj)
        else:
            statusCode = promotion_link(event, maglinkobj, tests)
        #remove link after consuming
        if statusCode['statusCode'] == 200:
            magiclinks.remove({"link":maglinkobj['link']})
        return statusCode

    return config.add_cors_headers({"statusCode":400,"body":"Invalid magiclink, try again"})
