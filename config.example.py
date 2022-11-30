from datetime import datetime, timezone, timedelta

# uri should contain auth and default database
DB_URI = "uri"
DB_COLLECTIONS = {
    "users": "users",
    "magic links": "magicLinks",
    "slack messages": "slackMessages"
}

SLACK_KEYS = {
    'token': '',
    'channel': ''
}

EMAIL_ADDRESS = ""
#Must use a generated app password for gmail
EMAIL_PASSWORD = ""

class GOOGLE_CAL:
    CAL_ID = ""
    CAL_API_KEY = ""


MAPS_API_KEY = ""


class TRAVEL:
    HACKRU_LOCATION = "New Brunswick, NJ, USA"
    MAX_REIMBURSE = 60
    CAR_RATE = {
        range(0, 50): 0,
        range(50, 101): 20,
        range(101, 201): 40,
        range(201, 2 ** 100000): 59.99
    }


# edt
TIMEZONE = timezone(timedelta(hours=-4))

AWS = {
    "aws_access_key_id": "AKI0f9jf209302jfjjfjfjfjfjfjfjfjfjfjfjfish",
    "aws_secret_access_key": "42069",
}
RESUME_BUCKET = "resumesf19"
WAIVER_BUCKET = "waiversf19"

# first is open second is close
REGISTRATION_DATES = [
    # open for registration
    [datetime(2018, 9, 19, tzinfo=TIMEZONE),
     datetime(2018, 10, 6, 10, tzinfo=TIMEZONE)],
    # reopen during the event of
    [datetime(2018, 10, 7, 12, tzinfo=TIMEZONE),
     datetime(2018, 10, 9, 12, tzinfo=TIMEZONE)]
]

# Json webtoken
JWT_SECRET = "D9E8A570628A0FC66D267B115BCA343EC31070D68124EA8003494B8676FE32A0"
JWT_ALGO = "HS256"
