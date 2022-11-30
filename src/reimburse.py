import requests as req
from pymongo import UpdateOne
from pymongo.errors import BulkWriteError
from src import util
import config
from src.schemas import ensure_schema, ensure_logged_in_user, ensure_role


# credit to https://stackoverflow.com/a/434328/5292630
def chunker(seq, size):
    return (seq[pos:pos + size] for pos in range(0, len(seq), size))


def req_matrix_and_clean(params):
    """
    Function used to make a Google API call to fetch the distances
    """
    def elem_to_dist(elem):
        if elem['status'] != 'OK':
            return 0
        else:
            return elem['distance']['value']
    # Google API is called using the below link with the configured parameters for each mode of transportation
    # and all the sources and destination
    MATRIX_BASE_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"
    got = req.get(MATRIX_BASE_URL, params=params)
    # raises an error is one occurred by calling the Google API
    got.raise_for_status()
    # otherwise, fetches the JSON received as response
    mat = got.json()
    # error checking to ensure request was successful
    if mat['status'] != 'OK':
        raise ValueError(mat)
    # converts the results into a dictionary where the key is the address and the value is the distance, if it was
    # successfully given from the Google API, otherwise it's defaulted to 0
    return {val: elem_to_dist(mat['rows'][idx]['elements'][0]) for idx, val in enumerate(mat['origin_addresses'])}


def req_distance_matrices(users):
    """
    Function used to create distance matrices where one axis represents the mode of transportation: car, bus and train
    while the other axis represents all the unique addresses of hackers
    """
    acc = {"car": dict(), "bus": dict(), "train": dict()}

    # Google API calls are broken apart into 25 users at a time
    for sub_users in chunker(users, 25):
        # determines all the unique locations that this 25 size subset of users travelled from and concatenates them,
        # separating each by a "|" (so that it can be sent along with the Google API request)
        origins = "|".join(u['travelling_from']['formatted_addr'] for u in sub_users
                           if u['travelling_from']['formatted_addr'] not in acc['car'])
        destinations = config.TRAVEL.HACKRU_LOCATION
        if origins == "":  # don't do a request if there are no unique origins
            continue

        # Google API parameters are created using the relevant information for each mode of transportation
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

        # the distance matrix is updated to include new addresses and their distances for each mode of transportation
        # where the distance comes from making a call to Google API (see req_matrix_and_clean)
        acc['car'].update(req_matrix_and_clean(car_params))
        acc['train'].update(req_matrix_and_clean(train_params))
        acc['bus'].update(req_matrix_and_clean(bus_params))

    # the entire distance matrix is returned after all the distances have been fetched
    return acc


def users_to_reimburse(lookup, users):
    """
    Function that creates a table of how much reimbursement each of the given users should receive as well as the sum
    total of all the reimbursement to be handed out
    """
    total = 0
    table = dict()
    # for each reimbursement-eligible hacker...
    for user in users:
        # if they are driving to the HackRU, then their reimbursement is calculated as follows
        # first the distance from their origin to the HackRU is fetched from the given distance matrix (lookup)
        # next that distance is multiplied by 2 (since it's a round-trip) and divided by 1609.344
        # (to convert from meters to miles)
        # finally depending on the range that total distance value falls within, the reimbursement is determined using
        # the values set in the config
        if user['travelling_from']['mode'] == 'car':
            dist = lookup[user['travelling_from']['mode']].get(user['travelling_from']['formatted_addr'], 0)
            dist = round(2*dist/1609.344)
            result = [config.TRAVEL.CAR_RATE[key] for key in config.TRAVEL.CAR_RATE if dist in key]
            reimburse = result[0]
        # otherwise, they are eligible for the max reimbursement set in the config
        else:
            reimburse = config.TRAVEL.MAX_REIMBURSE
        # the total is incremented to include the calculated reimbursement for the current user
        total += reimburse
        # and it's added to the table of reimbursements to be given out
        table[user['email']] = reimburse

    return table, total


@ensure_schema({
    "type": "object",
    "properties": {
        "token": {"type": "string"},
        "day-of": {"type": "boolean"}
    },
    "required": ["token"]
})
@ensure_logged_in_user()
@ensure_role([['director']])
def compute_all_reimburse(event, context, user=None):
    """
    Function used by a director to compute reimbursements
    """
    # all the relevant users are fetched by querying all hackers that are registered, have a travelling_from field and
    # have the addr_ready boolean set to True within the travelling_from object
    user_coll = util.coll('users')
    user_query = {"travelling_from": {"$exists": True}, "travelling_from.addr_ready": True,
                  "registration_status": "registered"}
    users = list(user_coll.find(user_query))

    # tries to create the distance matrix and error's out in-case of any Google API errors
    try:
        lookup = req_distance_matrices(users)
    except Exception as e:
        return {'statusCode': 512, 'body': repr(e)}
    # This line was purely for testing can be deleted if no more test are needed or have API key
    #lookup = None

    # uses the distance matrix to determine the reimbursements for each user and the sum total of all reimbursements
    table, total = users_to_reimburse(lookup, users)
    print(table)
    # uses bulk write to set the calculated reimbursement for each user within the database
    bulk_op = [UpdateOne({'email': email}, {'$set': {'travelling_from.reimbursement': table[email]}}) for email in table]
    try:
        data = user_coll.bulk_write(bulk_op, ordered=False)
        return {'statusCode': 200, 'mongo_result': data.bulk_api_result, 'total': total}
    except BulkWriteError as bwe:
        return {'statusCode': 512, 'body': bwe.details}
