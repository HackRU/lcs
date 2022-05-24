from testing_utils import *
from src import validate, authorize
import config
from datetime import datetime, timedelta

import pytest
import jwt
import json


@pytest.mark.run(order=3)
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
        "token": encoded_jwt.decode("utf-8"), # Encoded jwt is type bytes, json does not like raw bytes so convert to string
    }

    users = connect_to_db()
    users.update_one({'email': user_email}, {'$push': expired})

    val = validate.validate({'email': user_email, 'token': expired}, None)
    assert check_by_schema(schema_for_http(403, {"type": "string", "const": "Token invalid"}), val)
    
    # remove the token
    users.update_one({'email': user_email}, {'$pull': expired})
