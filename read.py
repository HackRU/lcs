import string
import json
import pymongo
from pymongo import MongoClient
import config
import hashlib

# assume frontend can parse userdata rendered from graphical menu to a MongoDB query

def read_info(event, context):
    client = MongoClient(config.DB_URI)

    db = client['camelot-test']
    db.authenticate(config.DB_USER, config.DB_PASS)

    tests = db['test']

    if context['role'] == 'director' or context['role'] == 'organizer':
        return list(tests.aggregate(event['query']))

    else:
        return tests.find_one(event['query'])

