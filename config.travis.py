from datetime import datetime, timezone, timedelta
import os


# uri should contain auth and default database
DB_URI_LOCAL = "mongodb://127.0.0.1:27017/travis"
DB_URI_ATLAS = os.getenv("DB_URI", "")
DB_URI = DB_URI_LOCAL

DB_COLLECTIONS = {
    "users": "users",
    "magic links": "magicLinks",
    "slack messages": "slackMessages"
}

SPARKPOST_KEY = os.getenv("SPARKPOST_KEY", "")

SLACK_KEYS = {
    'token': '',
    'channel': ''
}

class GOOGLE_CAL:
    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
    CLIENT_ID = os.getenv("GOOGLE_CAL_CLIENT_ID", "")
    CLIENT_SECRET = os.getenv("GOOGLE_CAL_CLIENT_SECRET", "")
    CAL_ID = os.getenv("GOOGLE_CAL_ID", "")

MAPS_API_KEY = os.getenv("MAPS_API_KEY", "")

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
    "aws_access_key_id": os.environ.get("AWS_ACCESS_KEY_ID"),
    "aws_secret_access_key": os.environ.get("AWS_SECRET_ACCESS_KEY"),
}
RESUME_BUCKET = "resumet"

# Json webtoken
JWT_SECRET = "1002C8E19420D4D5F117C13BC1971875F7CE4791ED0901A60E46549AAA74C80F"
JWT_ALGO = "HS256"