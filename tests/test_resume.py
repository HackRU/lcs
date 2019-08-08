import json

import authorize
import config
import resume

from pymongo import MongoClient
import pytest
import urllib3

email = "test@t.t"
pword = "jjjjjjjf"
token = ""
old_col = ""

def payload(email=email):
    return {"email": email, "token": token}

def setup_module(m):
    #temp change user collection
    global old_col
    old_col = config.DB_COLLECTIONS["users"]
    config.DB_COLLECTIONS["users"] = "test-users"

    #create a user
    result = authorize.create_user({"email": email, "password": pword}, {})
    if result["statusCode"] != 200:
        assert False
    global token
    token = result["body"]["auth"]["token"]

def teardown_module(m):
    #drop temp collection
    client = MongoClient(config.DB_URI)
    db = client[config.DB_NAME]
    db.authenticate(config.DB_USER,config.DB_PASS)
    db[config.DB_COLLECTIONS["users"]].drop()

    #reset colelction name
    global old_col
    config.DB_COLLECTIONS["users"] = old_col
    
def test_baduser():
    result = resume.upload_link(payload(email="foo"), {})
    assert result["statusCode"] == 400

def test_upload_ok():
    result = resume.upload_link(payload(), {})
    assert result["statusCode"] == 200

def test_download_ok():
    result = resume.download_link(payload(), {})
    assert result["statusCode"] == 200

def test_roundtrip():
    upload = resume.upload_link(payload(), {})["body"]["url"]
    download = resume.download_link(payload(), {})["body"]["url"]
    client = urllib3.PoolManager()
    stellar_resume = b'hire me pls'
    upload_res = client.request("PUT", upload, body=stellar_resume)
    assert upload_res.status == 200 or upload_res.status == 204

    download_res = client.request("GET", download)
    assert download_res.status == 200 or download_res.status == 204
    assert download_res.data == stellar_resume
    
