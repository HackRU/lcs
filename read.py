import string
import json
import pymongo
from pymongo import MongoClient
import config
from datetime import datetime
import dateutil.parser as dp

def validate_user(db, token, email):
    """
    Returns the user if the authtoken provided as token is valid.
    """
    if not token or not email:
        return False

    user = db.find_one({'email': email})
    if not any(i['token'] == token and datetime.now() < dp.parse(i['valid_until']) for i in user['auth']):
        return False

    return user

def read_info(event, context):
    """
    We allow for an arbitrary mongoose query to be passed in.
    If the aggregate field is present and true, we aggregate
    and otherwise "find_one."
    """

    if 'query' not in event or not event['query']:
        return config.add_cors_headers({"statusCode": 400, "body": "We query for your query."})
    #if aggregate is not present, it is false.
    if 'aggregate' not in event:
        event['aggregate'] = False

    client = MongoClient(config.DB_URI)

    db = client['lcs-db']
    db.authenticate(config.DB_USER, config.DB_PASS)

    tests = db['test']
    #get the user if they're logged in and making the request.
    user = validate_user(tests,
            event['token'] if 'token' in event else False,
            event['email'] if 'email' in event else False)

    #directors and organizers see all and know all
    if user and (user['role']['director'] or user['role']['organizer']):
        res_ = list(tests.aggregate(event['query'])) if event['aggregate'] else list(tests.find(event['query']))
    #users can see anything about themselves - in a find.
    elif user and not event['aggregate']:
        res_ = [res for res in tests.find(event['query']) if res['email'] == event['email']]
    #redact! Don't give public/non-organizers access to sensitive aggregations.
    else:
        restricted_fields = ['auth', 'mlhid', 'email', 'first_name', 'last_name', 'date_of_birth', 'email', 'password', 'id', 'github', 'resume', 'short_answer', 'data_sharing', 'rules_and_conditions']

        res_ = tests.aggregate(event['query']) if event['aggregate'] else list(tests.find(event['query']))
        for abstracted_data in restricted_fields:
            for doc in res_:
                if abstracted_data in doc:
                    del doc[abstracted_data]

    if not event['aggregate']:
        for i in res_:
            del i['_id']

    return config.add_cors_headers({"statusCode": 200, "body": res_})
