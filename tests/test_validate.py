from testing_utils import *

import authorize
import validate
import config

import pytest
import json

@pytest.mark.run(order=3)
def test_validate_token():
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
    assert check_by_schema(schema_for_http(200, {"type": "object", "const": user_dict}), val)

    #failures
    val = validate.validate({'email': user_email + 'fl', 'token': token}, None)
    assert check_by_schema(schema_for_http(400, {"type": "string", "const": "User not found"}), val)
    val = validate.validate({'email': user_email, 'token': token + 'fl'}, None)
    assert check_by_schema(schema_for_http(400, {"type": "string", "const": "Token not found"}), val)
    val = validate.validate({'emil': user_email, 'token': token + 'fl'}, None)
    assert check_by_schema(schema_for_http(400, {"type": "string"}), val)
    val = validate.validate({'email': user_email, 'oken': token + 'fl'}, None)
    assert check_by_schema(schema_for_http(400, {"type": "string"}), val)
