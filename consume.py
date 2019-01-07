import random
from pymongo import MongoClient
import validate
import config
import string
from datetime import datetime, timedelta
import bcrypt

def updateUserFromMagicLink(userCollection,maglinkobj,event):
    """
        Updates User Based on a magic link
    """
    #if the user forgot, then read the password and change it
    if maglinkobj['forgot'] == True:
        pass_ = event['password']
        pass_ = bcrypt.hashpw(pass_.encode('utf-8'), bcrypt.gensalt(rounds=8))
        checkifmlh = userCollection.find_one({"email":maglinkobj['email']})
        if not checkifmlh:
            return config.add_cors_headers({
                "statusCode": 400,
                "body": "We could not find that email."
            })
        userCollection.update_one({"email":maglinkobj['email']},{'$set':{'password':pass_}})
        return config.add_cors_headers({"statusCode":200,"body":"Sucessfully updated your password"})
    #else we want an auth token and an email
    else:
        ret_ = validate.get_validated_user(event)
        if ret_[0]:
           #Grab the permissions object
            permissions = maglinkobj['permissions']
            for i in permissions:
                if i == 'director':
                    userCollection.update_one({'email':event['email'] }, {'$set':{'role.director':True}})
                elif i == 'judge':
                    userCollection.update_one({'email':event['email'] }, {'$set':{'role.judge':True}})
                elif i == 'organizer':
                    userCollection.update_one({'email':event['email'] }, {'$set':{'role.organizer':True}})
                elif i == 'volunteer':
                    userCollection.update_one({'email':event['email'] }, {'$set':{'role.volunteer':True}})
                elif i == 'mentor':
                    userCollection.update_one({'email':event['email'] }, {'$set':{'role.mentor':True}})

            return config.add_cors_headers({"statusCode":200,"body":"Successfully updated your role"})
        else:
            return config.add_cors_headers({"statusCode":400,"body":"Failed to update: please login again."})

def consumeUrl(event,context):
    """
        Lambda function to consume a url. Queries the database and checks permissions and updates accordingly
    """
    if 'link' not in event:
        return config.add_cors_headers({"statusCode":400,"body":"No magic link provided"})

    client = MongoClient(config.DB_URI)
    db = client[config.DB_NAME]
    db.authenticate(config.DB_USER,config.DB_PASS)
    #user collection
    tests = db[config.DB_COLLECTIONS['users']]
    #maglink collection
    magiclinks = db[config.DB_COLLECTIONS['magic links']]
    maglinkobj = magiclinks.find_one({"link":event['link']})
    if maglinkobj:
        statusCode = updateUserFromMagicLink(tests,maglinkobj,event)
        #remove link after consuming
        if statusCode['statusCode'] == 200:
            magiclinks.remove({"link":maglinkobj['link']})
        return statusCode

    return config.add_cors_headers({"statusCode":400,"body":"Invalid magiclink, try again"})
