import json
from src import util

def hello(event, context):
    #print(f"YOU HAVE {event}")
    return util.add_cors_headers({"statusCode":202, "body": json.dumps("Response!")})