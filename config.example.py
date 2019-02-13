import datetime as d

DB_URI = "ein URL"
DB_USER = "un usuario"
DB_PASS = "el llave secreto"
DB_NAME = "lcs-db"
DB_COLLECTIONS = {
    "users": "test",
    "magic links": "maglinks",
    "slack messages": "slack-msgs"
}

MLH = {
    'client_id': 'an ID',
    'client_secret': 'ssh. It\'s a secret',
    'redirect_uri': 'where do we go now?',
    #As a matter of fact, the below needn't change.
    'grant_type': 'authorization_code'
}

SLACK_KEYS = {
    'token': '',
    'channel': ''
}

GOOGLE_CAL_ID = ""
MAPS_API_KEY=""

class TRAVEL:
    HACKRU_LOCATION = "New Brunswick, NJ, USA"
    MAX_REIMBURSE = 60
    MULTIPLIERS = {
        "car": 0.22 / 1609,
        "train": 0.66 / 1609,
        "bus": 0.3775 / 1609,
        "plane": 1 #doesn't matter - makes the code handy.
    }

# I'm too lazy with the EDT off-by-1 here...it won't impact day-of.
TIMEZONE = d.timezone(d.timedelta(hours=-5))
# See is_registration_open for how to use this: every time marks a toggle in the state.
REGISTRATION_DATES = [
        d.datetime(2018, 9, 19, tzinfo=TIMEZONE),
        d.datetime(2018, 10, 6, 10, tzinfo=TIMEZONE),
        d.datetime(2018, 10, 7, 12, tzinfo=TIMEZONE)]
def is_registration_open():
    i = 0
    time = d.datetime.now(d.timezone.utc)
    while i < len(REGISTRATION_DATES) and time >= REGISTRATION_DATES[i]:
        i += 1
    return i % 2 == 0

def add_cors_headers(resp):
    """
    Adds headers to allow for cross-origin requests.

    Not gonna lie, stackoverflow told us to do it
    and it works. We don't know how or why.
    """
    if 'headers' not in resp:
        resp['headers'] = dict()
    resp['headers']['Access-Control-Allow-Origin'] = '*',
    resp['headers']['Access-Control-Allow-Headers'] ='Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
    resp['headers']['Access-Control-Allow-Credentials'] = True,
    return resp

