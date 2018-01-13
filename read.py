import string
import json
import pymongo
from pymongo import MongoClient
import config
import hashlib

# input JSON-documents for MongoDB query (aggregation queries only work if director or organizer)
# NOTE: don't need to do hard error-checking - will be implemented by another script and not directly by the user, so it probably can't be broken.

def read_info(query, role):
    client = MongoClient(config.DB_URI)

    db = client['camelot-test']
    db.authenticate(config.DB_USER, config.DB_PASS)

    tests = db['test']

    if role == 'director' or role == 'organizer':
        return list(tests.aggregate(query))

    else:
        return tests.find_one(query)

