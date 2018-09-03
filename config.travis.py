DB_URI="127.0.0.1:27017"
DB_USER="creep"
DB_PASS="@radiohead.ed"
DB_NAME = "lcs-db"
DB_COLLECTIONS = {
    "users": "test",
    "magic links": "maglinks",
    "slack messages": "slack-msgs"
}

SPARKPOST_KEY="not yet supported"

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

