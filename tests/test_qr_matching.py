from testing_utils import *
from pymongo import MongoClient
import qrscan
import config
import validate
import authorize
import pytest
import json
import requests

email = "organizer@email.com"
pwrord = "1234567"
token = ""
old_col = ""
qr = "1j12jj1lkjlk;12j3kl4jlk13j4lkj12lk4jlkj1;lj4lkljjl1234jjlk234lj234jl23jl2oi3u4oiu12hhj1h1h1"

hckemail = "hacker@email.com"
hckword = "123456"
hcktoken = ""

def payload(auth_email=email):
	return {"auth_email" : auth_email,
		"token" : token,
		"email" : hckemail,
		"qr_code" : qr} 

def setup_module(m):
	global old_col 
	old_col = config.DB_COLLECTIONS["users"]
	config.DB_COLLECTIONS["users"] = "test-users"
	#db = util.get_db()
	#db["test-users"]
		
	result = authorize.create_user({"email": email, "password": pwrord}, {})
	assert result["statusCode"] == 200
	global token
	token = result["body"]["auth"]["token"]
	db = util.coll("users")
	updete = db.update_one({"email":email}, {"$set" : { "role" : { "hacker" : False , "organizer" : True}}})
	assert updete.modified_count >= 1
	
	result = authorize.create_user({"email": hckemail, "password": hckword}, {})
	assert result["statusCode"] == 200
	hcktoken = result["body"]["auth"]["token"]
	
def teardown_module(m):
	db = util.get_db()
	db[config.DB_COLLECTIONS["users"]].drop()

	global old_col
	config.DB_COLLECTIONS["users"] = old_col

def test_bad_role():
	result = qrscan.qrMatch(payload(auth_email=hckemail), {})
	assert result["statusCode"] == 400

def test_qr_match():
	result = qrscan.qrMatch(payload(), {})
	assert result["statusCode"] == 200
	db = util.coll("users")
	assert db.find_one({"email" : hckemail})["qrcode"][0] == qr

