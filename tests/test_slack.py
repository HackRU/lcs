from src import authorize, util
import json

import config
from src.slack import generate_dm_link

# credentials of the generator
email = "generator@test.com"
password = "temp_password"
token = None
slack_id = "U0407CVP9K8"

# credentials of the other user
other_email = "other@test.com"
other_password = "secure_password"
other_slack_id = "U040B24NB0V"

# collections and database
old_col = None
db = None

payload = None

current_slack_key = ""


# helper method to unset the slack id in the db document identified by slack_email
def unset_slack_id(slack_email):
    update = db.update_one({"email": slack_email}, {"$unset": {"slack_id": 1}})
    assert update.modified_count >= 1


# helper method to set the slack id to the slack_id_to_set in the db document identified by email_to_set
def set_slack_id(email_to_set, slack_id_to_set):
    update = db.update_one({"email": email_to_set}, {"$set": {"slack_id": slack_id_to_set}})
    assert update.modified_count >= 1


# method that sets up the module in preparation for running the tests
def setup_module(m):
    # import globals and switch the collection to a temporary collection
    global old_col, token, db, payload, current_slack_key
    old_col = config.DB_COLLECTIONS["users"]
    config.DB_COLLECTIONS["users"] = "test-users"

    # swap the key to be fetched from environment variable
    current_slack_key = config.SLACK_KEYS["token"]

    # create a dummy user
    result = authorize.create_user({"email": email, "password": password}, {})
    assert result["statusCode"] == 200
    token = result["body"]["token"]

    payload = {
        "token": token,
        "other_email": other_email
    }

    # create another dummy user
    result = authorize.create_user({"email": other_email, "password": other_password}, {})
    assert result["statusCode"] == 200
    assert bool(config.SLACK_KEYS["token"])

    # sets the slack id in the db documents
    db = util.coll("users")
    set_slack_id(email, slack_id)
    set_slack_id(other_email, other_slack_id)


# tears down a module
def teardown_module(m):
    # drops the temp collection that was created
    global db, old_col, current_slack_key
    db = util.get_db()
    db[config.DB_COLLECTIONS["users"]].drop()
    config.DB_COLLECTIONS["users"] = old_col

    # restore the slack api key
    config.SLACK_KEYS["token"] = current_slack_key


def test_bad_token():
    response = generate_dm_link({"token": "bad token", "other_email": other_email}, {})
    assert response["statusCode"] == 403


def test_bad_other_email():
    response = generate_dm_link({"token": token, "other_email": "invalid@email.com"}, {})
    assert response["statusCode"] == 403


def test_misconfigured_slack_token():
    slack_token = config.SLACK_KEYS["token"]
    config.SLACK_KEYS["token"] = "bad slack token"
    response = generate_dm_link(payload, {})
    assert response["statusCode"] == 503
    config.SLACK_KEYS["token"] = slack_token


def test_missing_slack_id():
    unset_slack_id(email)
    response = generate_dm_link(payload, {})
    assert response["statusCode"] == 403
    set_slack_id(email, slack_id)

    unset_slack_id(other_email)
    response = generate_dm_link(payload, {})
    assert response["statusCode"] == 403
    set_slack_id(other_email, other_slack_id)


def test_invalid_slack_id():
    set_slack_id(email, "bad slack id")
    response = generate_dm_link(payload, {})
    assert response["statusCode"] == 503
    set_slack_id(email, slack_id)

    set_slack_id(other_email, "bad slack id")
    response = generate_dm_link(payload, {})
    assert response["statusCode"] == 503
    set_slack_id(other_email, other_slack_id)


def test_valid_use():
    response = generate_dm_link(payload, {})
    assert response["statusCode"] == 200
