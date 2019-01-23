import config
import json
import googlemaps
from datetime import datetime
from pymongo import MongoClient

def do_one_user(user, gmaps, db_conn):
    start_loc = user['travelling_from']['formatted_address']
    rac_address = config.TRAVEL.HACKRU_LOCATION
    mode = user['travelling_from']['mode']

    if mode not in ['car', 'plane']:
        values = gmaps.distance_matrix(
                origins = start_loc,
                destinations = rac_address,
                units = 'imperial',
                mode = 'transit',
                transit_mode = mode)['rows'][0]['elements'][0]['distance']['value']
    elif mode == 'plane':
        values = config.TRAVEL.MAX_REIMBURSE
    else:
        values = gmaps.distance_matrix(
            origins = start_loc,
            destinations = rac_address,
            units = 'imperial',
            mode = 'driving',
            traffic_model = 'best_guess')

    values *= config.TRAVEL.MULTIPLIERS[mode]
    values = min(values, config.TRAVEL.MAX_REIMBURSE)

    db_conn.update_one({"email": user['email']}, {"$set": {"travelling_from.reimbursement": values}})


@ensure_schema({
    "type": "object",
    "properties": {
        "email": {"type": "string", "format": "email"},
        "token": {"type": "string"},
    },
    "required": ["email", "token"]
})
@ensure_logged_in_user()
@ensure_role([['director']])
def compute_all_reimburse(event, context, user):

    client = MongoClient(config.DB_URI)
    db = client['lcs-db']
    db.authenticate(config.DB_USER,config.DB_PASS)
    tests = db[config.DB_COLLECTIONS['users']]

    gmaps = googlemaps.Client(key=config.maps_key)

    for user in tests.find({"travelling_from": {"$exists": True}}):
        do_one_user(user, gmaps)

    return {'statusCode': 200, 'body': 'yote'}

