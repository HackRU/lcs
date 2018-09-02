import string
import re
import json
import pymongo
from pymongo import MongoClient
import config
import requests
import dateutil.parser as dp
from datetime import datetime

def get_validated_user(event):
    if 'email' not in event or 'token' not in event:
        return (False, "Email or token not provided.")

    email = event['email']
    token = event['token']

    #connect to DB
    client = MongoClient(config.DB_URI)
    db = client['lcs-db']
    db.authenticate(config.DB_USER, config.DB_PASS)

    tests = db['test']

    #try to find our user
    results = tests.find_one({"email":email})
    if results == None or results == [] or results == ():
        return (False, "User not found")

    #if none of the user's unexpired tokens match the one given, complain.
    if not any(i['token'] == token and datetime.now() < dp.parse(i['valid_until']) for i in results['auth']):
        return (False, "Token not found")

    return (True, results)



def validate(event, context):
    """
    Given an email and token,
    ensure that the token is an
    unexpired token of the user with
    the provided email.
    """

    #we either expect the info in the cookie
    #or in the body.
    #Cookie takes precedence.
    if 'Cookie' in event:
        event = json.loads(event['Cookie'])
    else:
        event = json.loads(event['body'])

    #make sure we have all the info we need.
    if 'email' not in event or 'token' not in event:
        return config.add_cors_headers({"statusCode":400, "body":"Data not submitted."})

    email = event['email']
    token = event['token']

    #connect to DB
    client = MongoClient(config.DB_URI)
    db = client['lcs-db']
    db.authenticate(config.DB_USER, config.DB_PASS)

    tests = db['test']


    #try to find our user
    results = tests.find_one({"email":email})
    if results == None or results == [] or results == ():
        return config.add_cors_headers({"statusCode":400, "body":"Email not found.", "isBase64Encoded": False})


    #if none of the user's unexpired tokens match the one given, complain.
    if not any(i['token'] == token and datetime.now() < dp.parse(i['valid_until']) for i in results['auth']):
        return config.add_cors_headers({"statusCode":400, "body":"Authentication token is invalid.", "isBase64Encoded": False})

    return config.add_cors_headers({"statusCode":200,"body":event, "isBase64Encoded": False})

def validate_updates(user, updates, auth_usr = None):
    """
    Ensures that the user is being updated in a legal
    way. Invariants are explained at line 127 for most
    fields and 67 for the registration_status in detail.
    """
    #if the user updating is not provided, we assume
    #the user's updating themselves.
    if auth_usr is None: auth_usr = user

    #quick utilities: to reject any update or any update by a non-admin.
    say_no = lambda x, y, z: False
    nonessentials= lambda x, y, z:
    def say_no_to_non_admin(x, y, z):
        return auth_usr['role']['organizer'] or auth_usr['role']['director']

    def check_registration(old, new, op):
        """
        Ensures that an edge exists in the user state graph
        and that the edge can be traversed by this mode of update.
        "True" edges are traversible by the user or through an admin
        whereas "False" ones require admin intervention. We only '$set' this field.
        """
        state_graph = {
            "unregistered": { #unregistered = did not fill out all of application.
                "registered": True #they can fill out the application.
            },
            "registered": { #they have filled out the application.
                #all transitions out of this are through the voting
                #system are require admins to have voted.
                "rejected": False,
                "confirmation": False,
                "waitlist": False
            },
            "rejected": { #the user is "rejected". REMEMBER: they see "pending"
                #only an admin may check a user in.
                "checked-in": False
            },
            "confirmation": { #This is when a user may or may not RSVP.
                #they get to choose if they're coming or not.
                "coming": True,
                "not-coming": True
            },
            "coming": { #they said they're coming.
                #they may change their mind, but only we can finalize
                #things.
                "not-coming": True,
                "confirmed": False,
                "checked-in": False #TODO: remove when there are many waves
            },
            "not-coming": { #the user said they ain't comin'.
                #They can always make a better decision.
                #But only we can finalize their poor choice.
                "coming": True,
                "waitlist": False
            },
            "waitlist": { #They were waitlisted. (Didn't RSVP, or not-coming.)
                #Only we can check them in.
                "checked-in": False
            },
            "confirmed": { #They confirmed attendance and are guarenteed a spot!
                #But only we can check them in.
                "checked-in": False
            }
        }

        #the update is valid if it is an edge traversible in the current
        #mode of update.
        return old in state_graph and new in state_graph[old] \
                and (state_graph[old][new] or say_no_to_non_admin(1, 2, 3)) \
                and op == "$set"

    #for all fields, we map a regex to a function of the old and new value and the operator being used.
    #the function determines the validity of the update
    #We "and" all the regexes, so an update is valid for all regexes it matches,
    #not just one.
    validator = {
            #this is a Mongo internal. DO NOT TOUCH.
            '_id': say_no,
            #TODO: we have to figure out "forgot password"
            'password': say_no,
            #can't me self-made judge?
            'role\\.judge': say_no, #TODO: do magic links need these?
            #can't unmake hacker
            'role\\.hacker': say_no_to_non_admin,
            #can't self-make organizer or director
            'role\\.director': say_no_to_non_admin,
            'role\\.organizer': say_no_to_non_admin,
            #can't change email
            'email': say_no,
            #can't change your own votes
            'votes': say_no_to_non_admin,
            'votes_from': say_no_to_non_admin,
            'skipped_users': say_no_to_non_admin,
            #or MLH info
            'mlh': say_no,
            #no hacks on the role object
            '^role$': say_no,
            #no destroying the day-of object
            'day_of': say_no_to_non_admin,
            'day_of\\.[A-Za-z1-2_]+': say_no_to_non_admin,
            'registration_status': check_registration,
            #auth tokens are never given access
            'auth': say_no,
            #nonessentials
            'traveling_from\\.mode': lambda x,y,z: x in ('bus', 'train', 'car', 'plane'),
    }

    def find_dotted(key):
        """
        Traverse the dictionary, moving down the dots.
        (ie. role.mentor indicates the mentor field
        within the role object within the user).
        """
        curr = user
        for i in key.split('.'):
            if i not in curr:
                #We assume that abscence means the addition
                #of a new field, which we allow.
                return None
            curr = curr[i]
        return curr

    def validate(key, op):
        """
        Finds out if a key is present in the object.
        If it is, ensure that for each regex it matches
        (from the validator - line 127), the validator
        accepts the change. Returns a boolean.
        """
        usr_attr = find_dotted(key)
        for item in validator:
            if re.match(item, key) is not None:
                if not validator[item](usr_attr, updates[op][key], op):
                    return False
        return True

    return {i: {j: updates[i][j] for j in updates[i] if validate(j, i)} for i in updates}

def update(event, context):
    """
    Given a user email, an auth email, an auth token,
    and the dictionary of updates,
    performs all updates the authorised user (with email
    auth_email) can from "updates" on the user with email "user_email".
    """

    #ensure that all the info is there.
    if 'user_email' not in event or 'auth' not in event or 'auth_email' not in event:
        return config.add_cors_headers({"statusCode":400, "body":"Data not submitted."})

    u_email = event['user_email']
    a_email = event['auth_email']
    auth_val =  event['auth']

    #connect to the DB.
    client = MongoClient(config.DB_URI)
    db = client['lcs-db']
    db.authenticate(config.DB_USER, config.DB_PASS)

    tests = db['test']

    #try to authorise the user with email auth_email
    a_res = tests.find_one({"email": a_email})
    if a_res == None or a_res == [] or a_res == {}:
        return config.add_cors_headers({"statusCode":400,"body":"Auth email not found."})

    if not any(i['token'] == auth_val and datetime.now() < dp.parse(i['valid_until']) for i in a_res['auth']):
        return config.add_cors_headers({"statusCode":400, "body":"Authentication token not found."})

    #assuming the auth_email user is authorised, find the user being modified.
    if u_email == a_email:
        #save a query in the nice case.
        results = a_res
    #if the user is an admin, they may modify any user.
    elif a_res['role']['organizer'] or a_res['role']['director']:
        results = tests.find_one({"email":u_email})
    else:
        return config.add_cors_headers({"statusCode": 403, "body": "Permission denied"})

    #ensure that the user was indeed found.
    if results == None or results == [] or results == {}:
        return config.add_cors_headers({"statusCode":400,"body":"User email not found."})

    #validate the updates, passing only the allowable ones through.
    updates = validate_updates(results, event['updates'], a_res)

    #update the user and report success.
    tests.update_one({'email': u_email}, updates)
    return config.add_cors_headers({"statusCode":200, "body":"Successful request."})
