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
    BUDGET = 3000
    MULTIPLIERS = {
        # 1609 = meters per mile because google returns meters
        "car": 0.22 / 1609,
        "train": 0.66 / 1609,
        "bus": 0.3775 / 1609,
        "plane": 1 #doesn't matter - makes the code handy.
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
