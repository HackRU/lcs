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
    
    #encrypt password
    pass_ = bcrypt.hashpw(pass_.encode('utf-8'), bcrypt.gensalt())

    #DB connection
    client = MongoClient(config.DB_URI)
    db = client['lcs-db']
    db.authenticate(config.DB_USER,config.DB_PASS)

    tests = db['test']

    checkhash  = tests.find_one({"email":email})

    #If the user ever used MLH log in, they must always use MLH login.
    if checkhash is not None:
        if checkhash.get('mlh', False) and not is_mlh:
            return config.add_cors_headers({"statusCode":403,"body":"Please use MLH to log in."})
    
        if (not (bcrypt.checkpw(pass_, checkhash['password'].encode('utf-8')))) and (not is_mlh):
            return config.add_cors_headers({"statusCode":403,"Body":"Wrong Password"})

    token = str(uuid.uuid4())

    update_val = {"auth": {
            "token":token,
            "valid_until":(datetime.now() + timedelta(days=3)).isoformat()
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
    if 'hackingCookie' in event['queryStringParameters']:
        if 'Cookie' not in event:
            return config.add_cors_headers({"statusCode":403,"body":"No cookie found."})

        return config.add_cors_headers({"statusCode":200,"body":event['Cookie']})


    params = config.MLH.copy()
    if 'code' not in event['queryStringParameters']:
        #this is the primitive auth flow, we expect an access token.
        access_token = event['queryStringParameters'].get('access_token')
        if access_token is None:
            return config.add_cors_headers({"statusCode":400,"body":"MLH Troubles! No access token."})
    else:
        #the new auth flow: we swap and auth code for the access token.
        params['code'] = event['queryStringParameters']['code']
        access_tok_json = requests.post(MLH_TOK_BASE_URL, params=params).json()
        if 'access_token' in access_tok_json:
            access_token = access_tok_json['access_token']
        else:
            return config.add_cors_headers({"statusCode":400,"body":"MLH Troubles! No access token."})

    #with access token in hand, we may query MLH.
    mlh_user = requests.get(MLH_USER_BASE_URL, params={'access_token': access_token}).json()

    if mlh_user['status'] != 'OK':
        return config.add_cors_headers({"statusCode":400,"body":"MLH Troubles!"})

    #connect to our DB
    client = MongoClient(config.DB_URI)
    db = client['lcs-db']
    db.authenticate(config.DB_USER,config.DB_PASS)
    test = db['test']

    user = test.find_one({'email': mlh_user['data']['email']})
    if user == None or user == [] or user == ():
        #making new user here
        mlh_user['data']['mlh'] = True
        if 'school' in mlh_user['data'] and 'name' in mlh_user['data']['school']:
            mlh_user['data']['school'] = mlh_user['data']['school']['name']
        a = create_user(mlh_user['data'], context, True)
    else:
        #authorize a pre-existing user
        event['email'] = user['email']
        event['password'] = 'defacto'
        a = authorize(event, context, is_mlh = True)
    #we make "a" to be our inner response.
    #for the frontend, we must convert this to the relevant re-direct.

    a['headers']['Location'] = event['queryStringParameters'].get('redir', "https://hackru.org/dashboard.html?")
    if(a['statusCode'] == 200):
        a['headers']['Location'] += 'authdata=' + a['body']
    else:
        a['headers']['Location'] += 'error=' + 'Could not log you in. Be sure you signed up with MLH, not us.'
    a["statusCode"] = 301
    a['headers']['Set-Cookie'] = "authdata=" + a['body']+ ";Path=/"
    a['headers']['Content-Type'] = "application/json"
    #yes, this works! This is how the frontend will get the token.

    return a

def create_user(event, context, mlh = False):
    # check if valid email
    is_not_day_of = datetime.now().day != 21
    # if is_not_day_of:
    #    return config.add_cors_headers({"statusCode":400, "body":"Registration is closed."})

    try:
       email = validate_email(event['email'])
    except KeyError:
       return config.add_cors_headers({"statusCode":400, "body":"No email provided!"})

    #MLH users don't have a password with us.
    if mlh == True:
        event['password'] = "defacto"

    if 'password' not in event:
       return config.add_cors_headers({"statusCode":400, "body":"No password provided"})

    u_email = event['email']
    password = event['password']
    password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    #DB connection
    client = MongoClient(config.DB_URI)
    db = client['lcs-db']
    db.authenticate(config.DB_USER, config.DB_PASS)

    tests = db['test']

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
        "registration_status": event.get("registration_status", "waitlist" if not is_not_day_of else "unregistered"),
        "level_of_study": event.get("level_of_study", ""),
        "mlh": mlh, #we know this and the below too, depending on how the function is called.
        "day_of":{
            "checkIn": False
        }
    }

    tests.insert(doc)

    return authorize(event, context, mlh)
