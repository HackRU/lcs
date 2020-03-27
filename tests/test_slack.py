import authorize
import config
import util
from slack import generate_dm_link

email = "generator@test.com"
password = "temp_password"
token = None
slack_id = "U010WR7TMAQ"
other_email = "other@test.com"
other_password = "secure_password"
other_slack_id = "U010WRFRJ7N"
old_col = None
db = None

payload = None


def unset_slack_id(slack_email):
    update = db.update_one({"email": slack_email}, {"$unset": {"slack_id": 1}})
    assert update.modified_count >= 1


def set_slack_id(email_to_set, slack_id_to_set):
    update = db.update_one({"email": email_to_set}, {"$set": {"slack_id": slack_id_to_set}})
    assert update.modified_count >= 1


def setup_module(m):
    global old_col, token, db, payload
    old_col = config.DB_COLLECTIONS["users"]
    config.DB_COLLECTIONS["users"] = "test-users"

    result = authorize.create_user({"email": email, "password": password}, {})
    assert result["statusCode"] == 200
    token = result["body"]["auth"]["token"]
    payload = {
        "email": email,
        "token": token,
        "other_email": other_email
    }

    result = authorize.create_user({"email": other_email, "password": other_password}, {})
    assert result["statusCode"] == 200
    assert bool(config.SLACK_KEYS["token"])

    db = util.coll("users")
    set_slack_id(email, slack_id)
    set_slack_id(other_email, other_slack_id)


def teardown_module(m):
    global db, old_col
    db = util.get_db()
    db[config.DB_COLLECTIONS["users"]].drop()
    config.DB_COLLECTIONS["users"] = old_col


def test_bad_email():
    response = generate_dm_link({"email": "invalid@email.com", "token": token, "other_email": other_email}, {})
    assert response["statusCode"] == 403


def test_bad_token():
    response = generate_dm_link({"email": email, "token": "bad token", "other_email": other_email}, {})
    assert response["statusCode"] == 403


def test_bad_other_email():
    response = generate_dm_link({"email": email, "token": token, "other_email": "invalid@email.com"}, {})
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
    update = db.update_one({"email": email}, {"$set": {"slack_id": "bad slack id"}})
    assert update.modified_count >= 1
    response = generate_dm_link(payload, {})
    assert response["statusCode"] == 503
    set_slack_id(email, slack_id)

    update = db.update_one({"email": other_email}, {"$set": {"slack_id": "bad slack id"}})
    assert update.modified_count >= 1
    response = generate_dm_link(payload, {})
    assert response["statusCode"] == 503
    set_slack_id(other_email, other_slack_id)


def test_valid_use():
    response = generate_dm_link(payload, {})
    assert response["statusCode"] == 200
