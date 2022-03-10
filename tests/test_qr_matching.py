from src import authorize, util, qrscan

import config
import json
from testing_utils import *

email = "organizer@email.com"
pwrord = "1234567"
token = ""
old_col = ""
qr = "1j12jj1lkjlk;12j3kl4jlk13j4lkj12lk4jlkj1;lj4lkljjl1234jjlk234lj234jl23jl2oi3u4oiu12hhj1h1h1"

hckemail = "hacker@email.com"
hckword = "123456"
hcktoken = ""


payload = None


def setup_module(m):
    global old_col
    old_col = config.DB_COLLECTIONS["users"]
    config.DB_COLLECTIONS["users"] = "test-users"

    result = authorize.create_user({"email": email, "password": pwrord}, {})
    assert result["statusCode"] == 200
    global token, payload
    token = result["body"]["token"]
    payload = {
        "token": token,
        "link_email": hckemail,
        "qr_code": qr
    }

    db = util.coll("users")
    update = db.update_one({"email": email}, {"$set": {"role": {"hacker": False, "organizer": True}}})
    assert update.modified_count >= 1

    result = authorize.create_user({"email": hckemail, "password": hckword}, {})
    assert result["statusCode"] == 200
    global hcktoken
    hcktoken = result["body"]["token"]


def teardown_module(m):
    db = util.get_db()
    db[config.DB_COLLECTIONS["users"]].drop()

    global old_col
    config.DB_COLLECTIONS["users"] = old_col


def test_bad_role():
    result = qrscan.qr_match({
        "token": hcktoken,
        "link_email": hckemail,
        "qr_code": qr
    }, {})
    assert result["statusCode"] == 403


def test_qr_match():
    result = qrscan.qr_match(payload, {})
    assert result["statusCode"] == 200
    db = util.coll("users")
    assert db.find_one({"email": hckemail})["qrcode"][0] == qr


def test_attend():
    event = 'free_supreme_bricks'

    def attend(qr_code, again=False, token=token):
        return qrscan.attend_event({
            'token': token,
            'qr': qr_code,
            'again': again,
            'event': event
        }, {})

    def test(qr_code):
        # once
        result = attend(qr_code)
        assert result['statusCode'] == 200
        # twice fail because again was not allowed
        result = attend(qr_code)
        assert result['statusCode'] == 402
        # twice pass with again
        result = attend(qr_code, again=True)
        assert result['statusCode'] == 200

    # by email
    test(hckemail)

    # reset day_of
    users = util.coll('users')
    users.update_one({'email': hckemail}, {'$set': {'day_of.' + event: 0}})

    # by qr
    result = qrscan.qr_match(payload, {})
    assert result['statusCode'] == 200
    test(qr)

    # bad qr
    result = attend('this_inst_an_email_or_qr@gmail.com')
    assert result['statusCode'] == 404

    # bad privs
    result = attend(email, token=hcktoken)
    assert result['statusCode'] == 403
