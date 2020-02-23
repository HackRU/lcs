import json
import random
import string
import uuid
from datetime import datetime, timedelta, timezone

import requests
import bcrypt

import config
import consume
from schemas import *
import util

@ensure_schema({
    "type": "object",
    "properties": {
        "email": {"type": "string", "format": "email"},
        "password": {"type": "string"}
    },
    "required": ["email", "password"]
})
def authorize(event,context):
    """The authorize endpoint. Given an email
       and a password, validates the user. Upon
       validation, the user is granted a token which
       is returned with its expiry time.
       """

    email = event['email'].lower()
    pass_ = event['password']

    tests = util.coll('users')

    checkhash = tests.find_one({"email":email})

    if checkhash is not None:
        if not bcrypt.checkpw(pass_.encode('utf-8'), checkhash['password']):
            return util.add_cors_headers({"statusCode":403,"body":"Wrong Password"})
    else:
        return util.add_cors_headers({"statusCode":403,"body":"invalid email,hash combo"})

    token = str(uuid.uuid4())

    update_val = {"auth": {
            "token":token,
            "valid_until":(datetime.now() + timedelta(days=3)).isoformat()
        }
    }

    #append to list of auth tokens
    tests.update_one({"email":email},{"$push":update_val})

    #return the value pushed, that is, auth token with expiry time.
    #throw in the email for frontend.
    update_val['auth']['email'] = email
    ret_val = { "statusCode":200,"isBase64Encoded": False, "headers": { "Content-Type":"application/json" },"body" : update_val}
    return util.add_cors_headers(ret_val)

#NOT A LAMBDA
def authorize_then_consume(event, context):
    rv = authorize(event, context)
    if 'link' in event:
        consumption_event = {
            'link': event['link'],
            'token': json.loads(rv['body'])['auth']['token']
        }
        consume_val = consume.consumeUrl(consumption_event, None)
        if consume_val['statusCode'] != 200:
            rv['statusCode'] = 400
    return rv

@ensure_schema({
    "type": "object",
    "properties": {
        "email": {"type": "string", "format": "email"},
        "password": {"type": "string"},
        "link": {"type": "string"},
        "github": {"type": "string"},
        "major": {"type": "string"},
        "short_answer": {"type": "string"},
        "shirt_size": {"type": "string"},
        "first_name": {"type": "string"},
        "last_name": {"type": "string"},
        "dietary_restrictions": {"type": "string"},
        "special_needs": {"type": "string"},
        "date_of_birth": {"type": "string"},
        "school": {"type": "string"},
        "grad_year": {"type": "string"},
        "gender": {"type": "string"},
        "level_of_study": {"type": "string"},
        "ethnicity": {"type": "string"},
        "phone_number": {"type": "string"}
    },
    "required": ["email", "password"],
    "additionalFields": False
})
def create_user(event, context):
    if not is_registration_open() and 'link' not in event:
        return util.add_cors_headers({"statusCode": 403, "body": "Registration Closed!"})

    u_email = event['email'].lower()
    password = event['password']
    password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=8))

    tests = util.coll('users')

    #if a user of the same email exists, we complain.
    usr = tests.find_one({'email': u_email})
    if usr != None and usr != [] and usr != {}:
        if 'link' not in event:
            return util.add_cors_headers({"statusCode": 400, "body": "Duplicate user!"})
        return authorize_then_consume(event, context)

    #The goal here is to have a complete user.
    #Where ever a value is not provided, we put the empty string.
    doc = {
        "email": u_email,
        "role": { #we enforce that the user is a hacker.
            "hacker": True,
            "volunteer": False,
            "judge": False,
            "sponsor": False,
            "mentor": False,
            "organizer": False,
            "director": False
        },
        "votes": 0,
        "password": password,
        "github": event.get("github", ''),
        "major": event.get("major", ''),
        "short_answer": event.get("short_answer", ''),
        "shirt_size": event.get("shirt_size", ''),
        "first_name": event.get("first_name", ''),
        "last_name": event.get("last_name", ''),
        "dietary_restrictions": event.get("dietary_restrictions", ''),
        "special_needs": event.get("special_needs", ''),
        "date_of_birth": event.get("date_of_birth", ''),
        "school": event.get("school", ''),
        "grad_year": event.get("grad_year", ''),
        "gender": event.get("gender", ''),
        "registration_status": event.get("registration_status", "unregistered"),
        "level_of_study": event.get("level_of_study", ""),
        "day_of":{
            "checkIn": False
        }
    }

    tests.insert_one(doc)

    return authorize_then_consume(event, context)

def is_registration_open():
    """
    checks regisitration using the configs timezone
    """
    now = datetime.now(config.TIMEZONE)
    for period in config.REGISTRATION_DATES:
        if period[0] <= now and now <= period[1]:
            return True
    return False
