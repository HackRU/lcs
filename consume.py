from schemas import *
import config
import util

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
        if i in ['director', 'judge', 'volunteer', 'mentor', 'sponsor']:
            role_bit = 'role.' + i
            userCollection.update_one({'email': user['email']}, {'$set': {role_bit: True}})

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
    tests = util.coll('users')
    #maglink collection
    magiclinks = util.coll('magic links')
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

    return util.add_cors_headers({"statusCode":400,"body":"Invalid magiclink, try again"})
