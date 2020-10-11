import importlib
from functools import wraps


from src import read
from unittest.mock import patch


test_user = {
    "email": "test@hackru.org",
    "role": {
        "hacker": True,
        "volunteer": False,
        "judge": False,
        "sponsor": False,
        "mentor": False,
        "organizer": False,
        "director": False
    },
    "registration_status": "unregistered",
    "travelling_from": {
        "reimbursement": 10
    }
}

DUMMY_TOKEN = "dummy token"

test_aggregate_query = {
    "token": DUMMY_TOKEN,
    "query": {
        "fields": ["major"]
    },
    "aggregate": True
}

test_user_query = {
    "token": DUMMY_TOKEN
}

test_elevated_query = {
    "token": DUMMY_TOKEN,
    "query": {
        "email": "test@hackru.org"
    }
}

test_director_aggregate_query = {
    "token": DUMMY_TOKEN,
    "query": [
        {"$match": {"registration_status": "registered"}},
        {"$group": {"_id": None, "registered_people": {"$sum": "$amount"}}}
    ],
    "aggregate": True
}


def patched_ensure_logged_in_user(role=None):
    def ensure_logged_in_user():
        def wrapper(fn, *args, **kwargs):
            @wraps(fn)
            def wrapt(event, context, *args, **kwargs):
                tu = test_user.copy()
                roles = test_user["role"].copy()
                if role:
                    assert role in roles
                    roles[role] = True
                tu["role"] = roles
                return fn(event, context, tu, *args)
            return wrapt
        return wrapper
    return ensure_logged_in_user


def test_unauthenticated_read():
    res = read.read_info({}, {})
    assert res["statusCode"] == 400


@patch("src.schemas.ensure_logged_in_user", patched_ensure_logged_in_user())
def test_missing_query_aggregate_read():
    importlib.reload(read)
    tq = test_aggregate_query.copy()
    del tq["query"]
    res = read.read_info(tq, {})
    assert res["statusCode"] == 400
    assert str(res["body"]).startswith("Error in JSON: 'query' is a required property")


@patch("src.schemas.ensure_logged_in_user", patched_ensure_logged_in_user())
def test_invalid_aggregate_read():
    importlib.reload(read)
    tq = test_aggregate_query.copy()
    tq["query"] = {"email": "test@hackru.org"}
    res = read.read_info(tq, {})
    assert res["statusCode"] == 400
    assert str(res["body"]).startswith("Error in JSON: 'fields' is a required property")
    tq["query"] = {"fields": ["bad field"]}
    res = read.read_info(tq, {})
    assert res["statusCode"] == 400
    assert str(res["body"]).startswith("Error in JSON: 'bad field' is not one of")


@patch("src.schemas.ensure_logged_in_user", patched_ensure_logged_in_user())
def test_successful_aggregate_read():
    importlib.reload(read)
    res = read.read_info(test_aggregate_query, {})
    assert res["statusCode"] == 200


@patch("src.schemas.ensure_logged_in_user", patched_ensure_logged_in_user())
def test_successful_user_read():
    importlib.reload(read)
    res = read.read_info(test_user_query, {})
    assert res["statusCode"] == 200
    # user object is returned as first object in an array
    assert res["body"] == [test_user]


@patch("src.schemas.ensure_logged_in_user", patched_ensure_logged_in_user("organizer"))
def test_missing_query_aggregate_organizer_read():
    importlib.reload(read)
    tq = test_elevated_query.copy()
    del tq["query"]
    res = read.read_info(tq, {})
    assert res["statusCode"] == 400
    assert str(res["body"]).startswith("Error in JSON: 'query' is a required property")


@patch("src.schemas.ensure_logged_in_user", patched_ensure_logged_in_user("organizer"))
def test_invalid_aggregate_organizer_read():
    importlib.reload(read)
    tq = test_elevated_query.copy()
    tq["aggregate"] = True
    res = read.read_info(tq, {})
    assert res["statusCode"] == 400
    assert str(res["body"]).startswith("Error in JSON: 'fields' is a required property")


@patch("src.schemas.ensure_logged_in_user", patched_ensure_logged_in_user("organizer"))
def test_successful_organizer_read():
    importlib.reload(read)
    res = read.read_info(test_aggregate_query, {})
    assert res["statusCode"] == 200


@patch("src.schemas.ensure_logged_in_user", patched_ensure_logged_in_user("organizer"))
def test_successful_organizer_read():
    importlib.reload(read)
    res = read.read_info(test_elevated_query, {})
    assert res["statusCode"] == 200


@patch("src.schemas.ensure_logged_in_user", patched_ensure_logged_in_user("director"))
def test_missing_query_director_read():
    importlib.reload(read)
    tq = test_elevated_query.copy()
    del tq["query"]
    res = read.read_info(tq, {})
    assert res["statusCode"] == 400
    assert str(res["body"]).startswith("Missing parameter 'query'")


@patch("src.schemas.ensure_logged_in_user", patched_ensure_logged_in_user("director"))
def test_invalid_param_director_read():
    importlib.reload(read)
    tq = test_elevated_query.copy()
    tq["query"] = ["bad query"]
    res = read.read_info(tq, {})
    assert res["statusCode"] == 400
    assert str(res["body"]).startswith("Invalid parameter 'query'")


@patch("src.schemas.ensure_logged_in_user", patched_ensure_logged_in_user("director"))
def test_successful_director_read():
    importlib.reload(read)
    res = read.read_info(test_elevated_query, {})
    assert res["statusCode"] == 200


@patch("src.schemas.ensure_logged_in_user", patched_ensure_logged_in_user("director"))
def test_invalid_param_director_aggregate_read():
    importlib.reload(read)
    tq = test_director_aggregate_query.copy()
    tq["query"] = {"email": "test@hackru.org"}
    res = read.read_info(tq, {})
    assert res["statusCode"] == 400
    assert str(res["body"]).startswith("Invalid parameter 'query'")


@patch("src.schemas.ensure_logged_in_user", patched_ensure_logged_in_user("director"))
def test_successful_director_aggregate_read():
    importlib.reload(read)
    res = read.read_info(test_director_aggregate_query, {})
    assert res["statusCode"] == 200
