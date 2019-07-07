import jsonschema as js
import config
import util

import dateutil.parser as dp

from functools import wraps
from datetime import datetime

def ensure_schema(schema, on_failure = lambda e, c, err: {"statusCode": 400, "body": "Error in JSON: {}".format(err)}):
    js.Draft4Validator.check_schema(schema)
    def wrap(fn):
        @wraps(fn)
        def wrapt(event, context, *extras):
            try:
                js.validate(event, schema)
                return config.add_cors_headers(fn(event, context, *extras))
            except js.exceptions.ValidationError as e:
                return config.add_cors_headers(on_failure(event, context, e))
        return wrapt
    return wrap

def ensure_logged_in_user(email_key='email', token_key='token', on_failure = lambda e, c, m, *a: {"statusCode": 400, "body": m}):
    def rapper(fn):
        @wraps(fn)
        def wrapt(event, context, *args):
            email = event[email_key]
            token = event[token_key]

            tests = util.coll('users')

            #try to find our user
            results = tests.find_one({"email":email})
            if results is None or results == None or results == [] or results == ():
                return on_failure(event, context, "User not found", *args)

            #if none of the user's unexpired tokens match the one given, complain.
            if not any(i['token'] == token and datetime.now() < dp.parse(i['valid_until']) for i in results['auth']):
                return on_failure(event, context, "Token not found", *args)

            del results['_id']
            del results['password']
            return fn(event, context, results, *args)
        return wrapt
    return rapper

def ensure_role(roles, on_failure = lambda e, c, u, *a: {"statusCode": 403, "body": "User does not have priviledges."}):
    def ensure_auth_user(fn):
        @wraps(fn)
        def wrapt(event, context, user, *args):
            if all(any(user['role'].get(role, False) for role in options) for options in roles):
                return fn(event, context, user, *args)
            return on_failure(event, context, user, *args)
        return wrapt
    return ensure_auth_user
