import json
import random
import string
import uuid
from datetime import datetime, timedelta
import config
import pymongo
import requests
from pymongo import MongoClient
from validate_email import validate_email
import bcrypt

def authorize(event,context):
    """The authorize endpoint. Given an email
       and a password, validates the user. Upon
       validation, the user is granted a token which
       is returned with its expiry time.
       """

    if('email' not in event  or 'password' not in event):
        return ({"statusCode":400,"body":"Invalid Request"})

    email = event['email']
    pass_ = event['password']

    #DB connection
    client = MongoClient(config.DB_URI)
    db = client[config.DB_NAME]
    db.authenticate(config.DB_USER,config.DB_PASS)

    tests = db[config.DB_COLLECTIONS['users']]

    checkhash  = tests.find_one({"email":email})

    if checkhash is not None:
        if not bcrypt.checkpw(pass_.encode('utf-8'), checkhash['password']):
            return config.add_cors_headers({"statusCode":403,"body":"Wrong Password"})
    else:
        return config.add_cors_headers({"statusCode":403,"body":"invalid email,hash combo"})

    token = str(uuid.uuid4())

    update_val = {"auth": {
            "token":token,
            "valid_until":(datetime.now() + timedelta(days=3)).isoformat()
        }
    }

    #append to list of auth tokens
    tests.update_one({"email":event['email']},{"$push":update_val})

    #return the value pushed, that is, auth token with expiry time.
    #throw in the email for frontend.
    update_val['auth']['email'] = email
    ret_val = { "statusCode":200,"isBase64Encoded": False, "headers": { "Content-Type":"application/json" },"body" : json.dumps(update_val)}
    return config.add_cors_headers(ret_val)

def create_user(event, context, mlh = False):
    if not config.is_registration_open():
        return config.add_cors_headers({"statusCode": 403, "body": "Registration Closed!"})

    # check if valid email
    try:
       email = validate_email(event['email'])
    except KeyError:
       return config.add_cors_headers({"statusCode":400, "body":"No email provided!"})

    if 'password' not in event:
       return config.add_cors_headers({"statusCode":400, "body":"No password provided"})

    u_email = event['email']
    password = event['password']
    password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=8))

    #DB connection
    client = MongoClient(config.DB_URI)
    db = client[config.DB_NAME]
    db.authenticate(config.DB_USER, config.DB_PASS)

    tests = db[config.DB_COLLECTIONS['users']]

    #if a user of the same email exists, we complain.
    usr = tests.find_one({'email': u_email})
    if usr != None and usr != [] and usr != {}:
        return config.add_cors_headers({"statusCode": 400, "body": "Duplicate user!"})

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
        "school": event.get("school", "Rutgers University"),
        "grad_year": event.get("grad_year", ''),
        "gender": event.get("gender", ''),
        "registration_status": event.get("registration_status", "unregistered"),
        "level_of_study": event.get("level_of_study", ""),
        "day_of":{
            "checkIn": False
        }
    }

    tests.insert_one(doc)

    return authorize(event, context)
