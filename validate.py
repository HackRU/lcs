import string
import re
import json
import pymongo
from pymongo import MongoClient
import config
import requests
import dateutil.parser as dp
from datetime import datetime

def validate(event, context):
    if 'email' not in event or 'token' not in event:
        return config.add_cors_headers({"statusCode":400, "body":"Data not submitted."})

    email = event['email']
    token = event['token']

    client = MongoClient(config.DB_URI)
    db = client['camelot-test']
    db.authenticate(config.DB_USER, config.DB_PASS)

    tests = db['test']

    results = tests.find_one({"email":email})

    if results == None or results == [] or results == ():
        return config.add_cors_headers({"statusCode":400,body:"Email not found."})

    if not any(i['auth']['token'] == token and datetime.now() < dp.parse(i['auth']['valid_until']) for i in results['auth']['token']):
        return config.add_cors_headers({"statusCode":400,body:"Authentication token is invalid."})

    return config.add_cors_headers({"statusCode":200,"body":"Successful request."})

def validate_updates(user, updates, auth_usr = user):
    say_no = lambda x, y: False

    def say_no_to_non_admin(x, y):
        return auth_usr['role']['organizer'] or auth_usr['role']['director']

    def check_registration(old, new):
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
                    "confirmed": False
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

        return old in state_graph and new in state_graph[old] \
                and (state_graph[new][old] or say_no_to_non_admin(1, 2))
                #remember that say_no_to_non_admin ignores arguments.

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
            #or MLH info
            'mlh': say_no,
            #no hacks on the role object
            '^role$': say_no,
            #no destroying the day-of object
            'day_of': say_no_to_non_admin,
            'day_of\\.[A-Za-z1-2_]+': say_no_to_non_admin,
            'registration_status': check_registration
    }

    def validate(key):
        if key not in user:
            #we allow the addition of arbitrary keys,
            #just to make life easier.
            return True

        for item in validator:
            if re.match(item, key) is not None:
                return validator[item](user[key], updates[key])

    return {i: updates[i] for i in updates if validate(key)}

def update(event, context):
    if 'user_email' not in event or 'auth' not in event or 'auth_email' not in event:
        return config.add_cors_headers({"statusCode":400, "body":"Data not submitted."})

    u_email = event['user_email']
    a_email = event['auth_email']
    auth_val =  event['auth']

    client = MongoClient(config.DB_URI)
    db = client['camelot-test']
    db.authenticate(config.DB_USER, config.DB_PASS)

    tests = db['test']

    a_res = tests.find_one({"email": a_email})

    if a_res == None or a_res == [] or a_res == {}:
        return config.add_cors_headers({"statusCode":400,"body":"Auth email not found."})

    if not any(i['token'] == auth_val and datetime.now() < dp.parse(i['valid_until']) for i in a_res['auth']):
        return config.add_cors_headers({"statusCode":400, "body":"Authentication token not found."})

    if u_email == a_email:
        results = a_res
    elif a_res['role']['organizer'] or a_res['role']['director']:
        results = tests.find_one({"email":u_email})
    else:
        return config.add_cors_headers({"statusCode": 403, "body": "Permission denied"})

    if results == None or results == [] or results == {}:
        return config.add_cors_headers({"statusCode":400,"body":"User email not found."})

    updates = validate_updates(results, event['updates'], a_res)

    tests.update_one({'email': u_email}, {'$set': updates})

    return config.add_cors_headers({"statusCode":200, "body":"Successful request."})
