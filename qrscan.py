import json
from schemas import ensure_schema, ensure_logged_in_user
import pymongo
from config import *
from util import *

qr_input = {
	"type" : "object",
	"Properties" : {
		"auth_email" : {"type" : "string"},
		"token" : {"type" : "string"},
		"email" : {"type" : "string"},
		"qr_code" : {"type" : "string"}
	},
	"required" : ["auth_email", "token", "email", "qr_code"]
}

#def exists(email, client):
#	check = client.DBHERE.find('email' : email)
#	#Incomplete, use correct statement
#	if check:
#		return True
#	else
#		return False

def test():
	collection = coll("users")
	print("collection name: " + collection.name)
	print("collection database: " + collection.database)
	print("collection document count: " + collection.count_documents)

@ensure_schema(qr_input)
@ensure_logged_in_user(email_key = "auth_email", token_key = "token")
def qrMatch(event, context):
	collection = coll('users')
	result = collection.update_one({'email' : event["email"]}, {'$push' : {'qrcode' : event["qr_code"]}})
	if result.matched_count == 1: 
		return {
			"statusCode" : 200, "body" : 
				{"success" : True}
		}
	#{"status": db.update({'email' : email}, {'$push' : {'qrcode' : qr})
	else:
		return {
			"statusCode" : 500,
				"body" : "failed to upload QR into database"
		}
	
			
