import requests as req
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError

import random
import config
import util
from schemas import *

#credit to https://stackoverflow.com/a/434328/5292630
def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))

def req_matrix_and_clean(params):
    def elem_to_dist(elem):
        if elem['status'] != 'OK':
            return 0
        else:
            return elem['distance']['value']

    MATRIX_BASE_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"
    got = req.get(MATRIX_BASE_URL, params=params)
    got.raise_for_status()
    mat = got.json()
    if mat['status'] != 'OK':
        raise ValueError(mat)

    return {val: elem_to_dist(mat['rows'][idx]['elements'][0]) for idx, val in enumerate(mat['origin_addresses'])}

def req_distance_matrices(users):
    acc = {"car": dict(), "bus": dict(), "train": dict()}

    for sub_users in chunker(users, 25):
        origins = "|".join(u['travelling_from']['formatted_addr'] for u in sub_users \
                if u['travelling_from']['formatted_addr'] not in acc['car'])
        destinations = config.TRAVEL.HACKRU_LOCATION

        car_params = {
            "origins": origins,
            "destinations": destinations,
            "mode": "driving",
            "key": config.MAPS_API_KEY,
        }
        train_params = {
            "origins": origins,
            "destinations": destinations,
            "mode": "transit",
            "transit_mode": "train",
            "key": config.MAPS_API_KEY,
        }
        bus_params = {
            "origins": origins,
            "destinations": destinations,
            "mode": "transit",
            "transit_mode": "bus",
            "key": config.MAPS_API_KEY,
        }

        acc['car'].update(req_matrix_and_clean(car_params))
        acc['train'].update(req_matrix_and_clean(train_params))
        acc['bus'].update(req_matrix_and_clean(bus_params))

    return acc

def users_to_reimburse(lookup, users):
    total = 0
    table = dict()
    for user in users:
        if user['travelling_from']['mode'] == 'car':
            dist = lookup[user['travelling_from']['mode']].get(user['travelling_from']['formatted_addr'], 0)
            #I used random to test the code because I could not make an API key. Can be deleted
            #dist = random.randint(0,500)
            result = [config.TRAVEL.CAR_RATE[key] for key in config.TRAVEL.CAR_RATE if dist in key]
            reimburse = result[0]
        else:
            reimburse = config.TRAVEL.MAX_REIMBURSE
        total += reimburse
        table[user['email']] = reimburse

    return table, total

@ensure_schema({
    "type": "object",
    "properties": {
        "email": {"type": "string", "format": "email"},
        "token": {"type": "string"},
        "day-of": {"type": "boolean"}
    },
    "required": ["email", "token"]
})
@ensure_logged_in_user()
@ensure_role([['director']])
def compute_all_reimburse(event, context, user):
    tests = util.coll('users')

    if 'day-of' not in event or not event['day-of']:
        user_query = {"travelling_from": {"$exists": True}, "travelling_from.addr_ready": True, "registration_status": "registered"}
    else:
        user_query = {"travelling_from": {"$exists": True}, "travelling_from.addr_ready": True, "day_of.checkIn": True}

    users = list(tests.find(user_query))

    #I commented the next 4 lines during testing because it would give me an error since I didnt have an API key
    try:
        lookup = req_distance_matrices(users)
    except Exception as e:
        return {'statusCode': 512, 'body': repr(e)}
    #This line was purely for testing can be deleted if no more test are needed or have API key
    #lookup = None
    
    table, total = users_to_reimburse(lookup, users)
    print(table)
    bulk_op = [UpdateOne({'email':i}, {'$set': {'travelling_from.reimbursement': table[i]}}) for i in table]
    try:
        data = tests.bulk_write(bulk_op, ordered=False)
        return {'statusCode': 200, 'mongo_result': data.bulk_api_result, 'total': total}
    except BulkWriteError as bwe:
        return {'statusCode': 512, 'body': bwe.details}
