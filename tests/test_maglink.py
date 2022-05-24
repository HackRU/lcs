from testing_utils import *

from src import authorize, maglink

import pytest
import mock
import json

user_email = "creep@radiohead.ed"
user_pass = "love"


@pytest.mark.run(order=3)
@mock.patch('src.maglink.emails.send_email')
def test_forgot_password_link(mock_send_email):
    # Patch the send_email method to do nothing and always return success
    mock_send_email.return_value = {'statusCode': 200, 'body': ''}

    res = maglink.gen_magic_link({'email': user_email, 'forgot': True}, None)
    assert check_by_schema(schema_for_http(200, {"statusCode": 200, "body": "Forgot password link has been emailed to you"}), res)
    link = util.coll('magic links').find_one({'email': user_email})
    assert link is not None
    assert link['forgot'] is True


@mock.patch('src.maglink.emails.send_email')
def test_forgot_password_link_bad_email(mock_send_email):
    # Patch the send_email method to do nothing and always return success
    mock_send_email.return_value = {'statusCode': 200, 'body': ''}

    # Fail with email not belonging to any user
    res = maglink.gen_magic_link({'email': 'bogus', 'forgot': True}, None)
    assert check_by_schema(schema_for_http(400, {"statusCode": 400, "body": "Invalid email: please create an account."}), res)


@pytest.mark.run(order=3)
@mock.patch('src.maglink.emails.send_email')
def test_director_link(mock_send_email):
    # Patch the send_email method to do nothing and always return success
    mock_send_email.return_value = {'statusCode': 200, 'body': ''}

    target_email = "test@example.com"
    target_perms = ['director']

    # Add director role to the test user
    util.coll('users').update_one({'email': user_email}, {'$set': {'role.director': True}})

    auth = authorize.authorize({'email': user_email, 'password': user_pass}, None)

    token = auth['body']['token']
    res = maglink.gen_magic_link({'token': token, 'emailsTo': [target_email], 'permissions': target_perms}, None)

    assert check_by_schema(schema_for_http(403, {'statusCode': 200}), res)
    link = res['body'][0][0]
    assert util.coll('magic links').find_one({'link': link}) is not None

    # Remove the role after we're done
    util.coll('users').update_one({'email': user_email}, {'$set': {'role.director': False}})


@pytest.mark.run(order=3)
@mock.patch('src.maglink.emails.send_email')
def test_director_link_bad_perms(mock_send_email):
    # Patch the send_email method to do nothing and always return success
    mock_send_email.return_value = {'statusCode': 200, 'body': ''}

    target_email = "test@example.com"
    target_perms = ['director']

    # Fail without director role
    auth = authorize.authorize({'email': user_email, 'password': user_pass}, None)
    token = auth['body']['token']
    res = maglink.gen_magic_link({'token': token, 'emailsTo': [target_email], 'permissions': target_perms}, None)
    assert check_by_schema(schema_for_http(403, {'statusCode': 403, 'body': 'User does not have priviledges.'}), res)
