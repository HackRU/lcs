from testing_utils import *

import authorize
import validate
import config

import pytest
import json

@pytest.mark.run(order=3)
def validate_token():
    user_email = "creep@radiohead.ed"
    passwd = "love"
    usr_dict = {'email': user_email, 'password': passwd}
    auth = authorize.authorize(usr_dict, None)
    token = auth['body']['auth']['token']

    #make sure user exists
    user_dict = get_db_user(user_email)
    assert 'email' in user_dict and user_dict['email'] == user_email

    #success
    val = validate.validate({'email': user_email, 'token': token}, None)
    assert dict_includes(val, http_dict(statusCode=expect_eq(200), body=expect_eq(user_dict)))

    #failures
    val = validate.validate({'email': user_email + 'fl', 'token': token}, None)
    assert dict_includes(val, http_dict(statusCode=expect_eq(400), body=expect_eq("User not found")))
    val = validate.validate({'email': user_email, 'token': token + 'fl'}, None)
    assert dict_includes(val, http_dict(statusCode=expect_eq(400), body=expect_eq("Token not found")))
    val = validate.validate({'emil': user_email, 'token': token + 'fl'}, None)
    assert dict_includes(val, http_dict(statusCode=expect_eq(400), body=expect_eq("Email or token not provided.")))
    val = validate.validate({'email': user_email, 'oken': token + 'fl'}, None)
    assert dict_includes(val, http_dict(statusCode=expect_eq(400), body=expect_eq("Email or token not provided.")))
