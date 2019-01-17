import pymongo
from pymongo import MongoClient

import config
from schemas import *

def tidy_results(res):
    for i in res:
        del i['_id']
        del i['password']
    return res

@ensure_schema({
    "type": "object",
    "properties": {
        "query": {
            "type": "object",
            "properties":{
                "fields": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["major", "shirt_size", "dietary_restrictions", "school", "grad_year", "gender", "level_of_study", "ethnicity"]
                    },
                    "uniqueItems": True
                },
                "just_here": {"type": "boolean"}
            },
            "required": ['fields']
        },
        "aggregate": {"type": "boolean", "const": True}
    },
    "required": ["query"]
})
def public_read(event, context):
    fields = event['fields']
    match = {"$match": {"registration_status": ("checked-in" if event.get('just_here', False) else {"$ne": "unregistered"})}}
    group = {"$group": {"_id": {field: "$" + field for field in fields}, "total": {"$sum": 1}}}

    client = MongoClient(config.DB_URI)
    db = client[config.DB_NAME]
    db.authenticate(config.DB_USER,config.DB_PASS)
    tests = db[config.DB_COLLECTIONS['users']]

    return {"statusCode": 200, "body": list(tests.aggregate([match, group]))}

def user_read(event, context, user):
    if event.get('aggregate', False):
        return public_read(event, context)
    return {"statusCode": 200, "body": [user]}

@ensure_schema({
    "type": "object",
    "properties": {
        "email": {"type": "string", "format": "email"},
        "token": {"type": "string"},
        "query": {"type": "object"},
        "aggregate": {"type": "boolean"}
    },
    "required": ["query", "email", "token"]
})
@ensure_logged_in_user(on_failure = lambda e, c, u, *a: public_read(e, c))
@ensure_role([['director', 'organizer']], lambda e, c, u, *a: user_read(e, c, u))
def do_director(event, context, user):
    client = MongoClient(config.DB_URI)
    db = client[config.DB_NAME]
    db.authenticate(config.DB_USER,config.DB_PASS)
    tests = db[config.DB_COLLECTIONS['users']]

    if event.get('aggregate', False):
        return {"statusCode": 200, "body": list(tests.aggregate(event['query']))}
    return {"statusCode": 200, "body": tidy_results(list(tests.find(event['query'])))}

@ensure_schema({
    "type": "object",
    "properties": {
        "email": {"type": "string", "format": "email"},
        "token": {"type": "string"},
        "query": {"type": "object"},
        "aggregate": {"type": "boolean"}
    },
    "required": ["query"]
})
def read_info(event, context):
    """
    We allow for an arbitrary mongo query to be passed in.
    If the aggregate field is present and true, we aggregate
    and otherwise "find_one."
    """

    if 'email' in event and 'token' in event:
        return do_director(event, context)
    return public_read(event, context)
