import jsonschema as js
import util
import json

from dateutil.parser import parse

from functools import wraps
from datetime import datetime

def ensure_schema(schema, on_failure = lambda e, c, err: {"statusCode": 400, "body": json.dumps("Error in JSON: {}".format(err))}):
    """
    Wrapper function used to validate the schema and that the given JSON follows it
    """
    js.Draft4Validator.check_schema(schema)
    def wrap(fn):
        @wraps(fn)
        def wrapt(event, context, *extras):
            try:
                js.validate(event, schema)
                return util.add_cors_headers(fn(event, context, *extras))
            except js.exceptions.ValidationError as e:
                return util.add_cors_headers(on_failure(event, context, e))
        return wrapt
    return wrap

def ensure_logged_in_user(email_key='email', token_key='token',
                          on_failure=lambda e, c, m, *a: {"statusCode": 403, "body": json.dumps(m)}):
    """
    Wrapper function used to authorize user using email and an auth token
    """
    def rapper(fn):
        @wraps(fn)
        def wrapt(event, context, *args):
            email = event[email_key]
            token = event[token_key]
            users = util.coll('users')

            # try to find user
            user = users.find_one({'email': email})
            if user is None:
                return on_failure(event, context, 'User Not found', *args)

            # look for token
            tokens = list(filter(lambda auth: auth['token'] == token, user['auth']))
            if len(tokens) == 0 or datetime.now() > parse(tokens[0]['valid_until']):
                return on_failure(event, context, 'Token invalid', *args)

            del user['_id']
            del user['password']
            return fn(event, context, user, *args)
        return wrapt
    return rapper

def ensure_role(roles, on_failure = lambda e, c, u, *a: {"statusCode": 403, "body": json.dumps("User does not have priviledges.")}):
    """
    Wrapper function used to validate that a user has at least 1 role within each subset of the set of roles
    """
    def ensure_auth_user(fn):
        @wraps(fn)
        def wrapt(event, context, user, *args):
            if all(any(user['role'].get(role, False) for role in options) for options in roles):
                return fn(event, context, user, *args)
            return on_failure(event, context, user, *args)
        return wrapt
    return ensure_auth_user
