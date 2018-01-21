import string
import random
import json
import pymongo
from pymongo import MongoClient
import config
import requests
import hashlib
from datetime import datetime, timedelta
from validate_email import validate_email
import uuid

MLH_TOK_BASE_URL = 'https://my.mlh.io/oauth/token'
MLH_USER_BASE_URL = 'https://my.mlh.io/api/v2/user.json'

def authorize(event,context):
    if('email' not in event  or 'password' not in event):
        return ({"statusCode":400,"body":"Invalid Request"})

    email = event['email']
    pass_ = event['password']
    client = MongoClient(config.DB_URI)

    db = client['camelot-test']
    db.authenticate(config.DB_USER,config.DB_PASS)

    tests = db['test']

    dat = tests.find_one({"email":email, "hash_password":pass_})
    if dat == None or dat == [] or dat == ():
        return ({"statusCode":403,"body":"invalid email,hash combo"})

    # check if the hash is correct
    checkhash  = tests.find_one({"email":email})

    if(checkhash['hash_password'] != event['password']):
        return ({"statusCode":403,"Body":"Wrong Password"})

    token = str(uuid.uuid4())

    bod_ = {"authtoken":token}

    update_val = {"auth":
        {
            "token":token,
            "valid_until":(datetime.datetime.now() + timedelta(hours=3)).isoformat()
        }
    }

    tests.update({"email":event['email']},{"$push":update_val})

    #append to list of auth tokens
    ret_val = { "statusCode":200,"isBase64Encoded": False, "headers": { "Content-Type":"application/json" },"body" :json.dumps(bod_)}
    return ret_val

def mlh_callback(event, context):
    params = config.MLH.copy()
    if 'code' not in event['queryStringParameters']:
        access_token = event['queryStringParameters'].get('access_token')
        if access_token is None:
            return ({"statusCode":400,"body":"MLH Troubles! No access token."})
    else:
        params['code'] = event['queryStringParameters']['code']
        access_tok_json = requests.post(MLH_TOK_BASE_URL, params=params).json()
        access_token = access_tok_json['access_token']
        scopes = access_tok_json['scope']

    mlh_user = requests.get(MLH_USER_BASE_URL, params={'access_token': access_token}).json()

    if mlh_user['status'] != 'OK':
        return ({"statusCode":400,"body":"MLH Troubles!"})

    client = MongoClient(config.DB_URI)
    db = client['camelot-test']
    db.authenticate(config.DB_USER,config.DB_PASS)
    test = db['test']
    user = test.find_one({'email': mlh_user['data']['email']})
    if user == None or user == [] or user == ():
        #making new user here
        mlh_user['data']['role'] = 'hacker'
        mlh_user['data']['sp_pass'] = 'fudging Hari'
        return create_user(mlh_user['data'], context)
    else:
        #auth
        event['email'] = user['email']
        event['password'] = user['password']
        #Kosher?
        return authorize(event, context)


def create_user(event, context):
    # check if valid email
    try:
       email = validate_email(event['email'])
    except EmailNotValidError as e:
       return ({"statusCode":400, "body":e})
    except KeyError:
       return ({"statusCode":400, "body":"No email provided!"})

    if 'password' not in event:
       return ({"statusCode":400, "body":"No password provided"})

    u_email = event['email']
    password = event['password']

    client = MongoClient(config.DB_URI)
    db = client['camelot-test']
    db.authenticate(config.DB_USER, config.DB_PASS)

    tests = db['test']

    default_school = {
            #RU-RAH!
            "id": 2,
            "name": "Rutgers University"
    }

    doc = { "email": u_email,
            "role": {
                "hacker": True,
                "volunteer": False,
                "judge": False,
                "sponsor": False,
                "mentor": False,
                "organizer": False,
                "director": False
            },
            "password": password,
            "github": event.get("github", ''),
            "major": event.get("major", ''),
            "shirt_size": event.get("shirt_size", ''),
            "first_name": event.get("first_name", ''),
            "last_name": event.get("last_name", ''),
            "dietary_restrictions": event.get("dietary_restrictions", ''),
            "special_needs": event.get("special_needs", ''),
            "date_of_birth": event.get("date_of_birth", ''),
            "school": event.get("school", default_school),
            "grad_year": event.get("grad_year", ''),
            "gender": event.get("gender", ''),
            "registration_status": event.get("registration_status", 0),
            "level_of_study": event.get("level_of_study", ""),
          }

    tests.insert(doc)

    return authorize(event, context)

# context param should have info of accessor account

def change_password(event, context):
    if event['password'].len() < 8:
        return ({"statusCode":200, "body":"invalid password"})

    client = MongoClient(config.DB_URI)

    db = client['camelot-test']
    db.authenticate(config.DB_USER, config.DB_PASS)

    tests = db['test']

    tests.update({"email": context['email'], "$push":{"password": hashlib.md5(event['password'].encode('utf-8')).hexdigest()}})

    return authorize(event, context)
