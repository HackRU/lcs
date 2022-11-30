from testing_utils import *

import config
import json
from src import validate, authorize

import pytest
from datetime import datetime, timedelta
import time


def has_token_for(thing):
    if 'body' not in thing:
        return False
    return check_by_schema(schema_for_http(200, {
        "type": "object",
        "properties": {
            "token": {"type": "string"}
        },
        "required": ["token"]
    }), thing)


def test_bad_email():
    user_email = "team@nonruhackathon.notemail.com"
    passwd = "arghf"
    usr_dict = {'email': user_email, 'password': passwd}
    auth = authorize.authorize(usr_dict, None)
    assert check_by_schema(schema_for_http(403, {"type": "string", "const": "invalid email,hash combo"}), auth)


def test_registration_open():
    # born too late to explore the planet
    config.REGISTRATION_DATES = [[
        datetime.now(config.TIMEZONE) + timedelta(hours=-2),
        datetime.now(config.TIMEZONE) + timedelta(hours=-1)
    ]]
    assert not authorize.is_registration_open()

    # born too early to explore the universe
    config.REGISTRATION_DATES = [[
        datetime.now(config.TIMEZONE) + timedelta(hours=+1),
        datetime.now(config.TIMEZONE) + timedelta(hours=+2)
    ]]
    assert not authorize.is_registration_open()

    # born just in time to register for HackRU
    config.REGISTRATION_DATES = [[
        datetime.now(config.TIMEZONE) + timedelta(hours=-1),
        datetime.now(config.TIMEZONE) + timedelta(hours=+1)
    ]]
    assert authorize.is_registration_open()

    # day of
    config.REGISTRATION_DATES = [
        [datetime.now(config.TIMEZONE) + timedelta(hours=-6),
         datetime.now(config.TIMEZONE) + timedelta(hours=-5)],
        [datetime.now(config.TIMEZONE) + timedelta(hours=-1),
         datetime.now(config.TIMEZONE) + timedelta(hours=+1)],
    ]
    assert authorize.is_registration_open()


@pytest.mark.run(order=1)
def test_creation():
    # open registration
    if not authorize.is_registration_open():
        config.REGISTRATION_DATES = [
            [datetime.now(config.TIMEZONE) + timedelta(hours=-6),
             datetime.now(config.TIMEZONE) + timedelta(hours=+6)]
        ]
    assert authorize.is_registration_open()

    user_email = "creep@radiohead.ed"
    passwd = "love"
    usr_dict = {'email': user_email, 'password': passwd}
    delete_user()
    auth = authorize.create_user(usr_dict, None)
    assert has_token_for(auth)


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
    # we guarantee the string value here since we produce the error message
    assert check_by_schema(schema_for_http(400, {"type": "string", "const": "Duplicate user!"}), auth)

    # Fail if registration is closed
    config.REGISTRATION_DATES = [[
        datetime.now(config.TIMEZONE) + timedelta(hours=-2),
        datetime.now(config.TIMEZONE) + timedelta(hours=-1)
    ]]
    assert not authorize.is_registration_open()
    auth = authorize.create_user(usr_dict, None)
    assert check_by_schema(schema_for_http(403, {"statusCode": 403, "body": "Registration Closed!"}), auth)


@pytest.mark.run(order=2)
def test_login_success():
    user_email = "creep@radiohead.ed"
    passwd = "love"
    usr_dict = {'email': user_email, 'password': passwd}
    auth = authorize.authorize(usr_dict, None)
    assert has_token_for(auth)


@pytest.mark.run(order=2)
def test_bad_password():
    user_email = "creep@radiohead.ed"
    passwd = "wrong"
    usr_dict = {'email': user_email, 'password': passwd}
    auth = authorize.authorize(usr_dict, None)
    assert check_by_schema(schema_for_http(403, {"statusCode": 403, "body": "Wrong Password"}), auth)


@pytest.mark.run(order=4)
def delete_user():
    user_email = "creep@radiohead.ed"
    db = connect_to_db()
    db.delete_one({'email': user_email})


@pytest.mark.run(order=5)
def test_multi_tokens():
    # open registration
    if not authorize.is_registration_open():
        config.REGISTRATION_DATES = [
            [datetime.now(config.TIMEZONE) + timedelta(hours=-6),
             datetime.now(config.TIMEZONE) + timedelta(hours=+6)]
        ]
    assert authorize.is_registration_open()

    user_email = "creep@radiohead.ed"
    passwd = "love"
    usr_dict = {'email': user_email, 'password': passwd}
    delete_user()

    num_tests = 5

    tokens = [''] * num_tests

    # Create user
    auth = authorize.create_user(usr_dict, None)  # creates user and 1 token in db
    tokens[0] = auth['body']['token']

    # make sure we can validate user with token1
    val = validate.validate({'token': tokens[0]}, None)
    assert check_by_schema(schema_for_http(200, {"type": "object", "const": usr_dict}), val)

    for i in range(1, num_tests):  # create num_tests - 1  tokens and test them
        # we need to sleep 1s here because otherwise the jwts generated will be the exact same when run locally
        # this is because the token is essentially a function of time (in seconds)
        time.sleep(1)

        auth = authorize.authorize(usr_dict, None)  # authorize user and get new token, creates a second token in dbs
        tokens[i] = auth['body']['token']

        # sanity check to make sure all tokens are unique
        for j in range(i - 1):
            assert tokens[i] != tokens[j]

        # attempt to validate with new token
        val = validate.validate({'token': tokens[i]}, None)
        assert check_by_schema(schema_for_http(200, {"type": "object", "const": usr_dict}), val)
