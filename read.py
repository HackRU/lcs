import string
import json
import pymongo
from pymongo import MongoClient
import config
import hashlib

# assume frontend can parse userdata rendered from graphical menu to a MongoDB query
def validate_user(db, token, email):
    if not token:
        return False

    user = db.find_one({'email': email})

def read_info(event, context):
    client = MongoClient(config.DB_URI)

    db = client['camelot-test'].authenticate(config.DB_USER, config.DB_PASS)

    tests = db['test']

    if context['role'] == 'director' or context['role'] == 'organizer':
        return list(tests.aggregate(event['query'])) if event['aggregate'] else tests.find(event['query'])

    else:
        restricted_fields = ['mlhid', 'email', 'first_name', 'last_name', 'date_of_birth', 'email', 'password', 'id', 'github', 'resume', 'short_answer', 'data_sharing', 'rules_and_conditions']

        res_ = tests.aggregate(event['query']) if event['aggregate'] else tests.find(event['query'])
        for abstracted_data in restricted_fields:
            for doc in res_:
                if abstracted_data in doc:
                    del doc[abstracted_data]

        return res_
