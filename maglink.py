import random
import datetime
import string
from datetime import datetime, timedelta

import use_sparkpost
import config
import util
from schemas import *

DEFAULT_LINK_BASE =  'https://hackru.org/magic/{}'

def forgotUser(event, magiclinks, tests):
    user = tests.find_one({"email":event['email']})
    if user:
        magiclink = 'forgot-' +  ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        obj_to_insert = {}
        obj_to_insert['email'] = event['email']
        obj_to_insert['link'] = magiclink
        obj_to_insert['forgot'] = True
        obj_to_insert[ "valid_until"] = (datetime.now() + timedelta(hours=3)).isoformat()
        magiclinks.insert_one(obj_to_insert)
        link_base = event.get('link_base', DEFAULT_LINK_BASE)
        rv = use_sparkpost.send_email(event['email'], link_base.format(magiclink), 'forgot-password', None)
        if rv['statusCode'] != 200:
            return rv
        return config.add_cors_headers({"statusCode":200,"body":"Forgot password link has been emailed to you"})
    else:
        return config.add_cors_headers({"statusCode":400,"body":"Invalid email: please create an account."})

def directorLink(magiclinks, numLinks, event, user):
    links_list = []
    permissions = []
    for i in event['permissions']:
            permissions.append(i)
    for j in range(min(numLinks, len(event['emailsTo']))):
        magiclink = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        obj_to_insert = {}
        obj_to_insert['permissions'] = permissions
        obj_to_insert['email'] = event['emailsTo'][j]
        obj_to_insert['forgot'] = False
        obj_to_insert['link'] = magiclink
        obj_to_insert["valid_until"] = (datetime.now() + timedelta(hours=3)).isoformat()
        magiclinks.insert_one(obj_to_insert)
        link_base = event.get('link_base', DEFAULT_LINK_BASE)
        link = link_base.format(magiclink)
        sent = use_sparkpost.send_email(obj_to_insert['email'],magiclink, event.get('template', 'upgrade-user'), user)['body']
        links_list.append((magiclink, sent))
    return links_list

@ensure_schema({
    "type": "object",
    "properties": {
        "email": {"type": "string", "format": "email"},
        "token": {"type": "string"},
        "template": {"type": "string"},
        "link_base": {"type": "string"},
        "permissions": {"type": "array"},
        "emailsTo": {"type": "array"},
        "numLinks": {"type": "integer"}
    },
    "required": ["email", "token", "permissions", "emailsTo"]
})
@ensure_logged_in_user()
@ensure_role([['director']])
def do_director_link(event, magiclinks, user):
    numLinks = event.get('numLinks', 1)
    links_list = directorLink(magiclinks, numLinks, event, user)
    return config.add_cors_headers({"statusCode":200,"body":links_list})

@ensure_schema({
    "type": "object",
    "properties": {
        "email": {"type": "string", "format": "email"},
        "link_base": {"type": "string"},
    },
    "required": ["email"]
})
def genMagicLink(event, context):
    """
       The event object expects and email and  checks if it is a valid request to generate the magic link
    """
    tests = util.coll('users')
    magiclinks = util.coll('magic links')

    if 'forgot' in event:
        return forgotUser(event, magiclinks, tests)
    return do_director_link(event, magiclinks)
