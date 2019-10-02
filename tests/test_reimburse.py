import json

from pymongo import MongoClient
import pytest
import requests

import authorize
import config

from testing_utils import *
import util
import validate
import reimburse

email = "director77@gmail.com"
pword = "1234566"
token = ""
old_col = ""
#Path for json file where it contains a list of travelling_from fields
path_to_users = "/Users/chia/PythonWorkspace/lcs/tests/tr_data.json"
users = None

def payload(auth_email=email):
    return {"email" : email,
            "token" : token,
            "day-of": True}

def setup_module(m):
    db = util.get_db()
    db["test-users"].drop()

    global old_col
    old_col = config.DB_COLLECTIONS["users"]
    config.DB_COLLECTIONS["users"] = "test-users"
    
    result = authorize.create_user({"email": email, "password": pword}, {})
    assert result["statusCode"]== 200
    
    global token
    token = result["body"]["auth"]["token"]
    db = util.coll("users")
    updete = db.update_one({"email":email}, {"$set" : { "role" : { "hacker": False, "director" : True}}})
    assert updete.modified_count >= 1

    with open(path_to_users, "r") as f:
        global users
        users = json.load(f)
    
    count = 0
    for user in users:
        user["email"] = str(count) + "@gmail"
        result = authorize.create_user({"email" : user["email"], "password": pword},{})
        assert result["statusCode"] == 200
    
        result = db.update_one({'email': user["email"]}, {'$set': user})
        assert result.matched_count == 1
        result = db.update_one({'email': user["email"]}, {'$set': {'day_of.checkIn': True}})
        assert result.matched_count == 1
        count = count+1

def teardown_module(m):
    db = util.get_db()
    db[config.DB_COLLECTIONS["users"]].drop()

    global old_col
    config.DB_COLLECTIONS["users"] = old_col

def test_tr():
    result = reimburse.compute_all_reimburse(payload(), {})
    assert result['statusCode'] == 200
    
    db = util.coll("users")
    for user in users:
        if user["travelling_from"]["is_real"] == True:
            assert db.find_one({"email" : user["email"]})["travelling_from"]["reimbursement"] >= 0
