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

MLH_TOK_BASE_URL = 'https://my.mlh.io/oauth/token'
MLH_USER_BASE_URL = 'https://my.mlh.io/api/v2/user.json'

def authorize(event,context, is_mlh = False):
    """The authorize endpoint. Given an email
       and a password, validates the user. Upon
       validation, the user is granted a token which
       is returned with its expiry time.

       The optional is_mlh parameter is for the convenience
       of the mlh callback below so that it need not replicate
       token generation."""

    if('email' not in event  or 'password' not in event):
        return ({"statusCode":400,"body":"Invalid Request"})

    email = event['email']
    pass_ = event['password']

    #DB connection
    client = MongoClient(config.DB_URI)
    db = client['lcs-db']
    db.authenticate(config.DB_USER,config.DB_PASS)

    tests = db['test']

    #find the email-password pair.
    dat = tests.find_one({"email":email, "password":pass_})
    if dat == None or dat == [] or dat == ():
        return config.add_cors_headers({"statusCode":403,"body":"invalid email,hash combo"})

    # check if the hash is correct - this is double-checking
    checkhash  = tests.find_one({"email":email})

    #If the user ever used MLH log in, they must always use MLH login.
    if checkhash.get('mlh', False) and not is_mlh:
        return config.add_cors_headers({"statusCode":403,"body":"Please use MLH to log in."})

    if(checkhash['password'] != event['password']) and not is_mlh:
        return config.add_cors_headers({"statusCode":403,"Body":"Wrong Password"})

    token = str(uuid.uuid4())

    update_val = {"auth": {
            "token":token,
            "valid_until":(datetime.now() + timedelta(hours=3)).isoformat()
        }
    }

    #append to list of auth tokens
    tests.update({"email":event['email']},{"$push":update_val})

    #return the value pushed, that is, auth token with expiry time.
    #throw in the email for frontend.
    update_val['auth']['email'] = email
    ret_val = { "statusCode":200,"isBase64Encoded": False, "headers": { "Content-Type":"application/json" },"body" : json.dumps(update_val)}
    return config.add_cors_headers(ret_val)

def mlh_callback(event, context):
    params = config.MLH.copy()
    if 'code' not in event['queryStringParameters']:
        #this is the primitive auth flow, we expect and access token.
        access_token = event['queryStringParameters'].get('access_token')
        if access_token is None:
            return ({"statusCode":400,"body":"MLH Troubles! No access token."})
    else:
        #the new auth flow: we swap and auth code for the access token.
        params['code'] = event['queryStringParameters']['code']
        access_tok_json = requests.post(MLH_TOK_BASE_URL, params=params).json()
        access_token = access_tok_json['access_token']
        scopes = access_tok_json['scope']

    #with access token in hand, we may query MLH.
    mlh_user = requests.get(MLH_USER_BASE_URL, params={'access_token': access_token}).json()

    if mlh_user['status'] != 'OK':
        return ({"statusCode":400,"body":"MLH Troubles!"})

    #connect to our DB
    client = MongoClient(config.DB_URI)
    db = client['lcs-db']
    db.authenticate(config.DB_USER,config.DB_PASS)
    test = db['test']

    user = test.find_one({'email': mlh_user['data']['email']})
    if user == None or user == [] or user == ():
        #making new user here
        mlh_user['data']['mlh'] = True
        a = create_user(mlh_user['data'], context, True)
    else:
        #authorize a pre-existing user
        event['email'] = user['email']
        event['password'] = user['password']
        a = authorize(event, context, is_mlh = True)
    #we make "a" to be our inner response.
    #for the frontend, we must convert this to the relevant re-direct.

    if(a['statusCode'] == 200):
        a["statusCode"] = 301

        a['headers']['Set-Cookie'] = "authdata=" + a['body']+ ";Path=/"
        a['headers']['Location'] = "http://ec2-34-217-103-53.us-west-2.compute.amazonaws.com:3000/"

        a['headers']['Content-Type'] = "application/json"
        #yes, this works! This is how the frontend will get the token.
        #TODO: domain=.hackru.org on prod.

    return a

def create_user(event, context, mlh = False):
    # check if valid email
    try:
       email = validate_email(event['email'])
    except EmailNotValidError as e:
       return config.add_cors_headers({"statusCode":400, "body":e})
    except KeyError:
       return config.add_cors_headers({"statusCode":400, "body":"No email provided!"})

    #MLH users don't have a password with us.
    if mlh == True:
        event['password'] = "defacto"

    if 'password' not in event:
       return ({"statusCode":400, "body":"No password provided"})

    u_email = event['email']
    password = event['password']

    #DB connection
    client = MongoClient(config.DB_URI)
    db = client['lcs-db']
    db.authenticate(config.DB_USER, config.DB_PASS)

    tests = db['test']

    #if a user of the same email exists, we complain.
    usr = tests.find_one({'email': u_email})
    if usr != None and usr != [] and usr != {}:
        return config.add_cors_headers({"statusCode": 400, "body": "Duplicate user!"})

    default_school = {
            #RU-RAH!
            "id": 2,
            "name": "Rutgers University"
    }

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
        "school": event.get("school", default_school),
        "grad_year": event.get("grad_year", ''),
        "gender": event.get("gender", ''),
        "registration_status": event.get("registration_status", 0),
        "level_of_study": event.get("level_of_study", ""),
        "mlh": mlh, #we know this and the below too, depending on how the function is called.
        "day_of":{
            "checkIn": False
        }
    }

    tests.insert(doc)

    return authorize(event, context, mlh)

# context param should have info of accessor account

def change_password(event, context):
    #TODO: fixme.
    if event['password'].len() < 8:
        return config.add_cors_headers({"statusCode":200, "body":"invalid password"})

    client = MongoClient(config.DB_URI)

    db = client['lcs-db']
    db.authenticate(config.DB_USER, config.DB_PASS)

    tests = db['test']

    if len(list(tests.find({"role":{"hacker":True}}))) >= 500:
        return {"statusCode":403, "body":"Event capacity reached."}

    tests.update({"email": context['email'], "$push":{"password": hashlib.md5(event['password'].encode('utf-8')).hexdigest()}})

    return authorize(event, context)
