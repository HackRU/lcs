import json
from schemas import ensure_schema, ensure_logged_in_user, ensure_role
import pymongo
from config import *
from util import *

qr_input = {
    "type" : "object",
    "Properties" : {
        "auth_email" : {"type" : "string", "format" : "email"},
	"token" : {"type" : "string"},
	"email" : {"type" : "string"},
	"qr_code" : {"type" : "string"}
    },
    "required" : ["auth_email", "token", "email", "qr_code"]
}

def dbinfo():
    collection = coll("users")
    print("collection name: " + str(collection.name))
    print("collection database: " + str(collection.database))
    print("collection document count: " + str(collection.count_documents))

@ensure_schema(qr_input)
@ensure_logged_in_user(email_key = "auth_email")
@ensure_role([['director', 'organizer', 'volunteer']])
def qr_match(event, context, user=None):
    collection = coll('users')

    result = collection.update_one({'email' : event["email"]}, {'$push' : {'qrcode' : event["qr_code"]}})
    if result.matched_count == 1:
        return {
            "statusCode" : 200,
            "body" : "success"
        }
    else:
        return {
            "statusCode" : 404,
            "body" : "User not found"
        }

@ensure_schema({
    'type': 'object',
    'properties': {
        'auth_email': {'type': 'string', 'format': 'email'},
        'token': {'type': 'string'},
        'qr': {'type': 'string'},
        'event': {'type': 'string'},
        'again': {'type': 'boolean'}
    },
    'required': ['auth_email', 'token', 'qr', 'event']
})
@ensure_logged_in_user(email_key='auth_email')
@ensure_role([['director', 'organizer', 'volunteer']])
def attend_event(aws_event, context, user=None):
    users = coll('users')
    qr = aws_event['qr']
    event = aws_event['event']
    again = aws_event.get('again', False)

    def attend(user):
        if not again and user['day_of'].get(event, 0) > 0:
            return {'statusCode': 402, 'body': 'user already checked into event'}
        new_user = users.find_one_and_update({'email': user['email']},
                                             {'$inc': {'day_of.' + event: 1}},
                                             return_document=pymongo.ReturnDocument.AFTER)

        return {'statusCode': 200, 'body': {
            'email': user['email'],
            'new_count': new_user['day_of'][event]
        }}

    user = users.find_one({'email': qr})
    if user:
        return attend(user)

    user = users.find_one({'qrcode': qr})
    if user:
        return attend(user)

    return {'statusCode': 404, 'body': 'user not found'}
