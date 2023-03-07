import json
from datetime import datetime, timedelta
import bcrypt
import jwt
import config
from src.schemas import ensure_schema
from src import util, authorize, validate
from google.oauth2 import id_token
from google.auth.transport import requests

#figure out testing 
#consider hashing?
#access and refresh vs long live access
#security concerns
@ensure_schema({
    "type": "object",
    "properties": {
        "token": {"type": "string"}
        "password": {"type": "string"}
    },
    "required": ["token"]
})
def authorize_google(event, context):
    """Initial endpoint hit for Google sign-in. 
    Receives id token that will be validated.
    Also has to check if user has been created or not (if not, it will automatically create)
    Also does check for legacy account, if so link the two (but client needs to include password)
     """
    #Last point: Or do we let users have two seperate accounts? (One with google signin and one password auth)
       #but currently impossible since we rely on email as unique for most endpoints
        #but then do we give option of only google-signin accounts to have passwords?
    token = event["token"]
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), config.GOOGLE_CLIENT_ID)
        print(idinfo)
        #safe to use id token since comes froom google (and verified)
        email  = idinfo["email"]
        google_id = idinfo['googleId']
        # fetch the collection that stores user data
        user_coll = util.coll('users')
        # fetch the data associated with the given email
        checkid = user_coll.find_one({"email": email})

        # if the data was found, case of legacy account or signin is successful 
        if checkid is not None:
            #case of successful signin (user already has google sign-in)
            #sanity check to make sure matches with mongo doc
            if "google_id" in checkid and \
            checkid['google_id'] == google_id: 
                return authorize(email)
            #case of legacy user using google sign-in on previously created hackru accnt
            elif "google_id" not in checkid and \
            'password' in event and \
            'password' in checkid: 
                body = {
                    'email': email,
                    'password': checkid['password']
                }
                val = authorize.authorize(body, None)
                #succesful authorization of email,pass -> link accounts
                if val['statusCode'] == 200:
                    user_coll.update_one({"email": email}, {"$set": {"google_id": google_id}})
                    return val
                #failure (prob bad password)
                else:
                    return val
            elif:
                return util.add_cors_headers({"statusCode": 403, "body": "Account associated with email. Try again with associated password"})
            else:
                return util.add_cors_headers({"statusCode": 401, "body": "Bad or Incorrect token given"})
        # if no data is found associated with the given email, we create a new account
        else:
            res = create_google_user(idinfo, None)            
            return res
    except ValueError: 
        return util.add_cors_headers({"statusCode": 401, "body": "Bad or Incorrect token given"})   
    
    #flow forlegacy case is if they (existing account) want google sign-in, 
        #will need frontend to redirect to input password
        #hit endpoint again authorizing the password then linking googleid
            #frontend will need to pass id token and password to this endpoint


# NOT A LAMBDA AND MEANT FOR GOOGLE AUTH, taken from authorize.py 
def authorize(email):
    exp = datetime.now() + timedelta(days=3)
    payload = {
        "email": email,
        "exp": int(exp.timestamp()),
    }
    encoded_jwt = jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGO)
    update_val = {
        "token": encoded_jwt.decode("utf-8"), # Encoded jwt is type bytes, json does not like raw bytes so convert to string
    }
    # appends the newly generated token to the list of auth tokens associated with this user
    user_coll.update_one({"email": email}, {"$push": update_val})
    # return the value pushed, that is, auth token with expiry time.
    ret_val = {
        "statusCode": 200,
        "isBase64Encoded": False,
        "headers": {"Content-Type": "application/json"},
        "body": update_val
    }
    return util.add_cors_headers(ret_val)

#NOT MEANT TO BE A LAMBDA, still meant for google auth flow
@ensure_schema({
    "type": "object",
    "properties": {
        "email": {"type": "string", "format": "email"}
    },
    "required": ["email"]
})
def create_google_user(event, context):
    # if registration is closed and a link is not given, we complain
    if not authorize.is_registration_open() and 'link' not in event:
        return util.add_cors_headers({"statusCode": 403, "body": "Registration Closed!"})

    u_email = event['email'].lower()
    google_id = event['googleId']

    user_coll = util.coll('users')

    # the goal here is to have a complete user; where ever a value is not provided, we put the empty string
    doc = {
        "email": u_email,
        "role": {
            "hacker": True,
            "volunteer": False,
            "judge": False,
            "sponsor": False,
            "mentor": False,
            "organizer": False,
            "director": False
        },
        "votes": 0,
        #make sure if theres no password field, nothing breaks (esp update and read)
        "google_id": google_id, 
        "github": '',
        "major": '',
        "short_answer": '',
        "shirt_size": '',
        "first_name": '',
        "last_name": '',
        "dietary_restrictions": '',
        "special_needs": '',
        "date_of_birth": '',
        "school": '',
        "grad_year": '',
        "gender": '',
        "registration_status": '',
        "level_of_study": '',
        "day_of": {
            "checkIn": False
        }
    }

    user_coll.insert_one(doc)
    return authorize(u_email)

