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

def dbinfo():
	collection = coll("users")
	print("collection name: " + str(collection.name))
	print("collection database: " + str(collection.database))
	print("collection document count: " + str(collection.count_documents))

@ensure_schema(qr_input)
@ensure_logged_in_user(email_key = "auth_email")
def qrMatch(event, context, user=None):
	collection = coll('users')
	
	#User the user input to check for the position. Make sure its director and organizer	
	if not user["role"]["organizer"]:
		return {
			"statusCode" : 400, 
			"body" : "Permission Denied.  Not a organizer or director"
		}

	result = collection.update_one({'email' : event["email"]}, {'$push' : {'qrcode' : event["qr_code"]}})
	if result.matched_count == 1: 
		return {
			"statusCode" : 200, 
			"body" : 
				{"success" : True}
		}
	#{"status": db.update({'email' : email}, {'$push' : {'qrcode' : qr})
	else:
		return {
			"statusCode" : 500,
			"body" : "failed to upload QR into database"
		}
	
			
