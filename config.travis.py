from datetime import datetime, timezone, timedelta
import os


# uri should contain auth and default database
DB_URI_LOCAL = "mongodb://127.0.0.1:27017/travis"
DB_URI_ATLAS = os.getenv("TRAVIS_DB_URI", "")
DB_URI = DB_URI_LOCAL

DB_COLLECTIONS = {
    "users": "users",
    "magic links": "magicLinks",
    "slack messages": "slackMessages"
}

SPARKPOST_KEY = os.getenv("TRAVIS_SPARKPOST_KEY", "")

SLACK_KEYS = {
    'token': os.getenv("TRAVIS_SLACK_API_TOKEN_BOT"),
    'channel': os.getenv("TRAVIS_SLACK_CHANNEL_ID")
}

class GOOGLE_CAL:
    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
    CLIENT_ID = os.getenv("TRAVIS_GOOGLE_CAL_CLIENT_ID", "")
    CLIENT_SECRET = os.getenv("TRAVIS_GOOGLE_CAL_CLIENT_SECRET", "")
    CAL_ID = os.getenv("TRAVIS_GOOGLE_CAL_ID", "")

MAPS_API_KEY = os.getenv("TRAVIS_MAPS_API_KEY", "")

class TRAVEL:
    HACKRU_LOCATION = "New Brunswick, NJ, USA"
    MAX_REIMBURSE = 60
    CAR_RATE = {
        range(0,50) : 0,
        range(50,101) : 20,
        range(101,201) : 40,
        range(201,2**100000) : 59.99
    }

# edt
TIMEZONE = timezone(timedelta(hours=-4))

# first is open second is close
REGISTRATION_DATES = [
    # open for registration
    [datetime(2018, 9, 19, tzinfo=TIMEZONE),
     datetime(2018, 10, 6, 10, tzinfo=TIMEZONE)],
    # reopen during the event of
    [datetime(2018, 10, 7, 12, tzinfo=TIMEZONE),
     datetime(2020, 10, 9, 12, tzinfo=TIMEZONE)]
]

RESUME = {
    "aws_access_key_id": os.environ.get("TRAVIS_AWS_ACCESS_KEY_ID"),
    "aws_secret_access_key": os.environ.get("TRAVIS_AWS_SECRET_ACCESS_KEY"),
}
RESUME_BUCKET = "resumet"

# Json webtoken
JWT_SECRET  = os.getenv("TRAVIS_JWT_SECRET", "")
JWT_ALGO = os.getenv("TRAVIS_JWT_ALGO", "")