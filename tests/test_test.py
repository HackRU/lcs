from testing_utils import *

import authorize
import config

import pytest
import json

def http_dict_for_token(email):
    ret_val = {
        "statusCode": expect_eq(200),
        "body" : lambda v: dict_includes(json.loads(v), {
            "auth": lambda a: dict_includes(a, {
                "token": expect_exist,
                "valid_until": expect_exist,
                "email": expect_eq(email)
            })
        })
    }
    return http_dict(**ret_val)

def test_bad_password():
    user_email = "team@nonruhackathon.notemail.com"
    passwd = "arghf"
    usr_dict = {'email': user_email, 'password': passwd}
    auth = authorize.authorize(usr_dict, None)
    assert dict_includes(auth, http_dict(statusCode = 403, body = "invalid email,hash combo"))

@pytest.mark.run(order=1)
def test_creation():
    user_email = "creep@radiohead.ed"
    passwd = "love"
    usr_dict = {'email': user_email, 'password': passwd}
    auth = authorize.create_user(usr_dict, None)
    assert dict_includes(auth, http_dict_for_token(user_email))

def test_creation_fail_cases():
    user_email = "creep@radiohead.ed"
    passwd = "love"
    usr_dict = {'password': passwd}
    auth = authorize.create_user(usr_dict, None)
    assert dict_includes(auth, http_dict(statusCode = 400, body = "No email provided!"))

    usr_dict = {'email': user_email}
    auth = authorize.create_user(usr_dict, None)
    assert dict_includes(auth, http_dict(statusCode = 400, body = "No password provided"))

@pytest.mark.run(order=2)
def test_login_success():
    user_email = "creep@radiohead.ed"
    passwd = "love"
    usr_dict = {'email': user_email, 'password': passwd}
    auth = authorize.authorize(usr_dict, None)
    assert dict_includes(auth, http_dict_for_token(user_email))

    db = connect_to_db()
    db.delete_one({'email':user_email})
