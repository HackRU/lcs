import json
from datetime import datetime, timedelta
import bcrypt
import jwt
import config
from src.schemas import ensure_schema
from src import util, consume


@ensure_schema({
    "type": "object",
    "properties": {
        "email": {"type": "string", "format": "email"},
        "password": {"type": "string"}
    },
    "required": ["email", "password"]
})
def authorize(event, context):
    """The authorize endpoint. Given an email
       and a password, validates the user. Upon
       validation, the user is granted a token which
       is returned with its expiry time.
       """

    # extract the email and password from the given object
    email = event['email'].lower()
    pass_ = event['password']

    # fetch the collection that stores user data
    user_coll = util.coll('users')

    # fetch the data associated with the given email
    checkhash = user_coll.find_one({"email": email})

    # if the data was found, then password is verified
    if checkhash is not None:
        # if the hash of the given and stored password are different, then it's the wrong password
        if not bcrypt.checkpw(pass_.encode('utf-8'), checkhash['password']):
            return util.add_cors_headers({"statusCode": 403, "body": "Wrong Password"})
    # if no data is found associated with the given email, error is returned
    else:
        return util.add_cors_headers({"statusCode": 403, "body": "invalid email,hash combo"})
    # Build a JWT to use as an authentication token, put embedded within its payload the email
    # along with an expiration timestamp in the format of a js NumericDate (as that is what is required
    # for JWT's authentication scheme
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


# NOT A LAMBDA
def authorize_then_consume(event, context):
    rv = authorize(event, context)
    if 'link' in event:
        consumption_event = {
            'link': event['link'],
            'token': json.loads(rv['body'])['token']
        }
        consume_val = consume.consume_url(consumption_event, None)
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
    # if registration is closed and a link is not given, we complain
    if not is_registration_open() and 'link' not in event:
        return util.add_cors_headers({"statusCode": 403, "body": "Registration Closed!"})

    # extracts the email and password
    u_email = event['email'].lower()
    password = event['password']
    # password is hashed with a salt
    password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(rounds=8))

    # the collection of users is fetched
    user_coll = util.coll('users')

    # tries to query the collection for userdata for this email
    usr = user_coll.find_one({'email': u_email})
    # if some data associated with this email exists...
    if usr is not None:
        # if a link is not provided, the intention is assumed to be to create a new user but since a user with this
        # email already exists, we complain
        if 'link' not in event:
            return util.add_cors_headers({"statusCode": 400, "body": "Duplicate user!"})
        # otherwise, the user is authorized and link is consumed
        return authorize_then_consume(event, context)

    # the goal here is to have a complete user; where ever a value is not provided, we put the empty string
    doc = {
        "email": u_email,
        # we enforce that the user is a hacker
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
        "level_of_study": event.get("level_of_study", ''),
        "day_of": {
            "checkIn": False
        }
    }

    # inserts the newly created user into the collection
    user_coll.insert_one(doc)

    # calls the function to also consume any links provided
    return authorize_then_consume(event, context)


def is_registration_open():
    """
    Function used to check if registration is open using the timezone and registration dates specified within the config
    """
    now = datetime.now(config.TIMEZONE)
    # registration dates are specified as nested arrays, with each element of the outer array being an array of two
    # elements
    # each of these inner arrays specifies the start of the period as first element and end as the second element
    # if the instance right now is within any of those valid periods, registration is essentially open
    for period in config.REGISTRATION_DATES:
        if period[0] <= now <= period[1]:
            return True
    return False
