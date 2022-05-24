from src import authorize, util, reimburse
import json
import config

from testing_utils import *

email = "director77@gmail.com"
pword = "1234566"
token = ""
old_col = ""

users_result = [20, 0, 0, 60, 60, 40, 59.99]
users = [
    {
        "travelling_from": {
            "is_real": True,
            "mode": "car",
            "addr_ready": True,
            "formatted_addr": "Montclair, NJ, USA"

        }
    },
    {
        "travelling_from": {
            "is_real": False,
            "mode": None,
            "addr_ready": False,
            "formatted_addr": None
        }
    },
    {
        "travelling_from": {
            "is_real": True,
            "mode": "car",
            "addr_ready": True,
            "formatted_addr": "Princeton, NJ, USA"
        }
    },
    {
        "travelling_from": {
            "is_real": True,
            "mode": "bus",
            "addr_ready": True,
            "formatted_addr": "College Park, MD, USA"
        }
    },
    {
        "travelling_from": {
            "is_real": True,
            "mode": "train",
            "addr_ready": True,
            "formatted_addr": "Providence, RI, USA"
        }
    },
    {
        "travelling_from": {
            "is_real": True,
            "mode": "car",
            "addr_ready": True,
            "formatted_addr": "White Plains, NY, USA"
        }
    },
    {
        "travelling_from": {
            "is_real": True,
            "mode": "car",
            "addr_ready": True,
            "formatted_addr": "Cleveland, OH, USA"
        }
    }
]


def setup_module(m):
    db = util.get_db()
    db["test-users"].drop()

    global old_col
    old_col = config.DB_COLLECTIONS["users"]
    config.DB_COLLECTIONS["users"] = "test-users"

    result = authorize.create_user({"email": email, "password": pword}, {})
    assert result["statusCode"] == 200

    global token

    token = result["body"]["token"]

    db = util.coll("users")
    updete = db.update_one({"email": email}, {"$set": {"role": {"hacker": False, "director": True}}})
    assert updete.modified_count >= 1

    count = 0
    for user in users:
        user["email"] = str(count) + "@gmail"
        result = authorize.create_user({"email": user["email"], "password": pword}, {})
        assert result["statusCode"] == 200

        result = db.update_one({'email': user["email"]}, {'$set': user})
        assert result.matched_count == 1
        result = db.update_one({'email': user["email"]}, {'$set': {'registration_status': 'registered'}})
        assert result.matched_count == 1
        count = count + 1


def teardown_module(m):
    db = util.get_db()
    db[config.DB_COLLECTIONS["users"]].drop()

    global old_col
    config.DB_COLLECTIONS["users"] = old_col


def test_tr():
    result = reimburse.compute_all_reimburse({"token": token}, {})
    assert result['statusCode'] == 200

    db = util.coll("users")
    index = 0
    for user in users:
        if user["travelling_from"]["is_real"]:
            result = db.find_one({"email": user["email"]})
            assert result["travelling_from"]["reimbursement"] >= users_result[index]
        index = index + 1
