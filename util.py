import config
from functools import wraps
from pymongo import MongoClient


def add_cors_headers(resp):
    """
    Adds headers to allow for cross-origin requests.

    Not gonna lie, stackoverflow told us to do it
    and it works. We don't know how or why.
    """
    if 'headers' not in resp:
        resp['headers'] = dict()
    resp['headers']['Access-Control-Allow-Origin'] = '*',
    resp['headers']['Access-Control-Allow-Headers'] = 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
    resp['headers']['Access-Control-Allow-Credentials'] = True,
    return resp


def cors(f):
    """
    Wrapper function that adds CORS headers to the return value of the function that is being wrapped
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        resp = f(*args, **kwargs)
        return add_cors_headers(resp)
    return wrapper


_cached = None
def get_db():
    """
    if the database uri has a default db and auth info then getting a database doesn't
    have to involve a lot of config. also caches client so lambda can effectively use 
    connection pooling
    """
    global _cached
    if not _cached:
        _cached = MongoClient(config.DB_URI).get_database()
    return _cached


def coll(collname):
    return get_db()[config.DB_COLLECTIONS[collname]]
