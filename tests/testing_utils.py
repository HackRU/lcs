import sys
import json

sys.path.append("..")

from src import util
import jsonschema as js
import json
from copy import deepcopy


def connect_to_db():
    return util.coll('users')


def schema_for_http(status_code, body_schema):
    return {
        "type": "object",
        "properties": {
            "headers": {
                "type": "object",
                "required": ["Access-Control-Allow-Origin", "Access-Control-Allow-Headers", "Access-Control-Allow-Credentials"]
            },
            "statusCode": {
                "type": "integer",
                "const": status_code
            },
            "body": body_schema
        },
        "required": ["headers", "statusCode"]
    }


def check_by_schema(schema, thing):
    copy = deepcopy(thing)
    if 'body' in copy:
        copy['body'] = copy['body']
    js.validate(copy, schema)
    return True


def get_db_user(email):
    db = connect_to_db()
    return db.find_one({"email": email})
