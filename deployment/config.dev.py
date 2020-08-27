import os
from datetime import datetime, timezone, timedelta

# uri should contain auth and default database
DB_URI_LOCAL = os.getenv("DEVELOP_DB_URI", "")
DB_URI = DB_URI_LOCAL

DB_COLLECTIONS = {
    "users": "users",
    "magic links": "magicLinks",
    "slack messages": "slackMessages"
}

SPARKPOST_KEY = os.getenv("DEVELOP_SPARKPOST_KEY", "")

SLACK_KEYS = {
    'token': os.getenv("DEVELOP_SLACK_API_TOKEN"),
    'channel': os.getenv("DEVELOP_SLACK_CHANNEL_ID")
}


class GOOGLE_CAL:
    CAL_ID = os.getenv("DEVELOP_GOOGLE_CAL_ID", "")
    CAL_API_KEY = os.getenv("DEVELOP_GOOGLE_CAL_API_KEY", "")


MAPS_API_KEY = os.getenv("DEVELOP_MAPS_API_KEY", "")


class TRAVEL:
    HACKRU_LOCATION = "New Brunswick, NJ, USA"
    MAX_REIMBURSE = float(os.getenv("DEVELOP_MAX_REIMBURSE", ""))
    BUDGET = float(os.getenv("DEVELOP_TRAVEL_BUDGET", ""))
    MULTIPLIERS = {
        "car": float(os.getenv("DEVELOP_CAR_REIMBURSE", )),
        "train": float(os.getenv("DEVELOP_TRAIN_REIMBURSE", )),
        "bus": float(os.getenv("DEVELOP_BUS_REIMBURSE", )),
        "plane": float(os.getenv("DEVELOP_PLANE_REIMBURSE", ))  # doesn't matter - makes the code handy.
    }


# edt
TIMEZONE = timezone(timedelta(hours=-4))

# first is open second is close
REGISTRATION_DATES = [
    # always open for registration
    [datetime.now(TIMEZONE) + timedelta(days=-1),
     datetime.now(TIMEZONE) + timedelta(days=+1)]
]

RESUME = {
    "aws_access_key_id": os.environ.get("DEVELOP_AWS_ACCESS_KEY_ID"),
    "aws_secret_access_key": os.environ.get("DEVELOP_AWS_SECRET_ACCESS_KEY"),
}
RESUME_BUCKET = os.getenv("DEVELOP_RESUME_BUCKET", "")

# Json webtoken
JWT_SECRET = os.getenv("DEVELOP_JWT_SECRET", "")
JWT_ALGO = os.getenv("DEVELOP_JWT_ALGO", "")
