from testing_utils import *
from src import validate, authorize
import config
from datetime import datetime, timedelta

import pytest
import jwt
import json


@pytest.mark.run(order=1)
def test_validate_token():
    user_email = "creep@radiohead.ed"
    passwd = "love"
    usr_dict = {'email': user_email, 'password': passwd}
    auth = authorize.authorize(usr_dict, None)

    token = auth['body']['token']
    # make sure user exists

    user_dict = get_db_user(user_email)
    assert 'email' in user_dict and user_dict['email'] == user_email

    # success
    val = validate.validate({'token': token}, None)
    assert check_by_schema(schema_for_http(200, {"type": "object", "const": user_dict}), val)

    # failures
    val = validate.validate({'email': user_email, 'token': token + 'fl'}, None)
    assert check_by_schema(schema_for_http(403, {"type": "string", "const": "Token invalid"}), val)
    val = validate.validate({'oken': token}, None)
    assert check_by_schema(schema_for_http(403, {"type": "string"}), val)

    # create expired jwt
    exp = datetime.now() + timedelta()
    payload = {
        "email": user_email,
        "exp": int(exp.timestamp()),
    }

    encoded_jwt = jwt.encode(payload, config.JWT_SECRET, algorithm=config.JWT_ALGO)
    expired = {
        "token": encoded_jwt, # Encoded jwt is type bytes, json does not like raw bytes so convert to string
    }

    users = connect_to_db()
    users.update_one({'email': user_email}, {'$push': expired})

    val = validate.validate({'email': user_email, 'token': expired}, None)
    assert check_by_schema(schema_for_http(403, {"type": "string", "const": "Token invalid"}), val)
    
    # remove the token
    users.update_one({'email': user_email}, {'$pull': expired})

@pytest.mark.run(order=2)
def test_add_timestamp_when_registered_success():
    user_email = "creep@radiohead.ed"
    password = "love"
    user_dict = { 'email': user_email, "password": password}
    auth = authorize.authorize(user_dict, None)

    auth_token = auth['body']['token']

    # make sure the test subject and authorizer exists
    user_db = get_db_user(user_email)
    assert 'email' in user_db and user_db['email'] == user_email

    updates = {
        "$set": {
            "registration_status": "registered"
        }, 
        "$inc": {},
        "$push": {}
    }

    event = {
        "token": auth_token,
        "user_email": user_email, 
        "updates": updates
    }

    # success case
    # pylint: disable=no-value-for-parameter
    success = validate.update(event, None)
    assert check_by_schema(schema_for_http(200, {"type": "string", "const": "Successful request."}), success)
    confirm = get_db_user(user_email)
    assert 'registered_at' in confirm and confirm['registration_status'] == "registered"

    # revert the registration status back to how it is before (unregistered)
    users = connect_to_db()
    revert_updates = {
        "$set": {
            'registration_status': "unregistered"
        },
        "$unset": {
            'registered_at': 1
        }
    }
    users.update_one({'email': user_email}, revert_updates)    

@pytest.mark.run(order=3)
def test_add_timestamp_when_registered_failure():
    # case that won't add the timestamp 
    auth_email = "creep@radiohead.ed"
    auth_pass = "love"
    auth_dict = { 'email': auth_email, "password": auth_pass}
    auth = authorize.authorize(auth_dict, None)

    auth_token = auth['body']['token']
    auth_user = get_db_user(auth_email)
    assert "email" in auth_user and auth_user['email'] == auth_email

    updates = {
        "$set": {
            "grad_year": "2025"
        }, 
        "$inc": {},
        "$push": {}
    }

    event = {
        "token": auth_token,
        "user_email": auth_email, 
        "updates": updates
    }

    # pylint: disable=no-value-for-parameter
    failure = validate.update(event, None)
    assert check_by_schema(schema_for_http(200, {"type": "string", "const": "Successful request."}), failure)
    # no timestamp will be added because the update is completely unrelated to changing "registration_status" to "registered"
    confirm = get_db_user(auth_email)
    # make sure timestamp does not exist in this user's db
    assert "registered_at" not in confirm 

    # revert all updates that have been made in this test
    users = connect_to_db()
    revert_updates = {
        "$set": {
            "grad_year": ""
        }
    }
    users.update_one({'email': auth_email}, revert_updates)    
