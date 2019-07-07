from testing_utils import *

import authorize
import config

import pytest
import json
import datetime as d

def has_token_for(email, thing):
    if 'body' not in thing:
        return False
    return check_by_schema(schema_for_http(200, {
        "type": "object",
        "properties": {
            "auth": {
                "type": "object",
                "properties": {
                    "token": {"type": "string"},
                    "valid_until": {"type": "string"},
                    "email": {"type": "string", "const": email}
                },
                "required": ["token", "email", "valid_until"]
            }
        },
        "required": ["auth"]
    }), thing)

def test_bad_password():
    user_email = "team@nonruhackathon.notemail.com"
    passwd = "arghf"
    usr_dict = {'email': user_email, 'password': passwd}
    auth = authorize.authorize(usr_dict, None)
    assert check_by_schema(schema_for_http(403, {"type": "string", "const": "invalid email,hash combo"}), auth)

@pytest.mark.run(order=1)
def test_creation():
    now = d.datetime.now(d.timezone.utc)
    idx_of_time = list(
            i for i in enumerate(config.REGISTRATION_DATES + [d.datetime.now(d.timezone.utc)]) \
            if i[1] >= now)[0][0]
    assert (not authorize.is_registration_open()) == idx_of_time % 2

    #open registration
    if not authorize.is_registration_open():
        config.REGISTRATION_DATES = []
    assert authorize.is_registration_open()

    user_email = "creep@radiohead.ed"
    passwd = "love"
    usr_dict = {'email': user_email, 'password': passwd}
    auth = authorize.create_user(usr_dict, None)
    assert has_token_for(user_email, auth)

@pytest.mark.run(order=2)
def test_creation_fail_cases():
    user_email = "creep@radiohead.ed"
    passwd = "love"
    usr_dict = {'password': passwd}
    auth = authorize.create_user(usr_dict, None)
    assert check_by_schema(schema_for_http(400, {"type": "string"}), auth)

    usr_dict = {'email': user_email}
    auth = authorize.create_user(usr_dict, None)
    assert check_by_schema(schema_for_http(400, {"type": "string"}), auth)

    usr_dict = {'email': user_email, 'password': passwd}
    auth = authorize.create_user(usr_dict, None)
    #we guarantee the string value here since we produce the error message
    assert check_by_schema(schema_for_http(400, {"type": "string", "const": "Duplicate user!"}), auth)

@pytest.mark.run(order=2)
def test_login_success():
    user_email = "creep@radiohead.ed"
    passwd = "love"
    usr_dict = {'email': user_email, 'password': passwd}
    auth = authorize.authorize(usr_dict, None)
    assert has_token_for(user_email, auth)

@pytest.mark.run(order=4)
def delete_user():
    user_email = "creep@radiohead.ed"
    db = connect_to_db()
    db.delete_one({'email':user_email})
