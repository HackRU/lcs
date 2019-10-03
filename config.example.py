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

SPARKPOST_KEY = ""

class GOOGLE_CAL:
    SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]
    CLIENT_ID = ""
    CLIENT_SECRET = ""
    CAL_ID = ""

MAPS_API_KEY = ""

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

RESUME = {
    "aws_access_key_id": "AKI0f9jf209302jfjjfjfjfjfjfjfjfjfjfjfjfish",
    "aws_secret_access_key": "42069",
}
RESUME_BUCKET = "resumesf19"

# first is open second is close
REGISTRATION_DATES = [
    # open for registration
    [datetime(2018, 9, 19, tzinfo=TIMEZONE),
     datetime(2018, 10, 6, 10, tzinfo=TIMEZONE)],
    # reopen during the event of
    [datetime(2018, 10, 7, 12, tzinfo=TIMEZONE),
     datetime(2018, 10, 9, 12, tzinfo=TIMEZONE)]
]
