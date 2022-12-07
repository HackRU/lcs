from datetime import datetime, timezone, timedelta
import os


# uri should contain auth and default database
DB_URI = os.getenv("PRODUCTION_DB_URI", "")


DB_COLLECTIONS = {
    "users": "users",
    "magic links": "magicLinks",
    "slack messages": "slackMessages"
}

SPARKPOST_KEY = os.getenv("PRODUCTION_SPARKPOST_KEY", "")

SLACK_KEYS = {
    'token': os.getenv("PRODUCTION_SLACK_API_TOKEN"),
    'channel': os.getenv("PRODUCTION_SLACK_CHANNEL_ID")
}

EMAIL_ADDRESS = os.getenv("PRODUCTION_EMAIL_ADDRESS"),
EMAIL_PASSWORD = os.getenv("PRODUCTION_EMAIL_PASSWORD")

class GOOGLE_CAL:
    CAL_ID = os.getenv("PRODUCTION_GOOGLE_CAL_ID", "")
    CAL_API_KEY = os.getenv("PRODUCTION_GOOGLE_CAL_API_KEY", "")

MAPS_API_KEY = os.getenv("PRODUCTION_MAPS_API_KEY", "")

# Currently not used as reimbursement is disabled
# class TRAVEL:
#     HACKRU_LOCATION = "New Brunswick, NJ, USA"
#     MAX_REIMBURSE = float(os.getenv("PRODUCTION_MAX_REIMBURSE", ""))
#     BUDGET = float(os.getenv("PRODUCTION_TRAVEL_BUDGET", ""))
#     MULTIPLIERS = {
#         "car": float(os.getenv("PRODUCTION_CAR_REIMBURSE", )),
#         "train":  float(os.getenv("PRODUCTION_TRAIN_REIMBURSE", )),
#         "bus": float(os.getenv("PRODUCTION_BUS_REIMBURSE", )),
#         "plane":  float(os.getenv("PRODUCTION_PLANE_REIMBURSE", ))
#     }

# edt
TIMEZONE = timezone(timedelta(hours=-4))

# first is open second is close, currently registration dates are not open information
REGISTRATION_DATES = [
    # open for registration
    [datetime(int(os.getenv("PRODUCTION_START_YEAR", )), int(os.getenv("PRODUCTION_START_MONTH", )), int(os.getenv("PRODUCTION_START_DAY", )), tzinfo=TIMEZONE),
     datetime(int(os.getenv("PRODUCTION_END_YEAR", )), int(os.getenv("PRODUCTION_END_MONTH", )), int(os.getenv("PRODUCTION_END_DAY", )), int(os.getenv("PRODUCTION_END_HOUR", )), tzinfo=TIMEZONE)],
    # reopen during the event of
    [datetime(int(os.getenv("PRODUCTION_DAY_OF_START_YEAR", )), int(os.getenv("PRODUCTION_DAY_OF_START_MONTH", )), int(os.getenv("PRODUCTION_DAY_OF_START_DAY", )), int(os.getenv("PRODUCTION_DAY_OF_START_HOUR", )), tzinfo=TIMEZONE),
     datetime(int(os.getenv("PRODUCTION_DAY_OF_END_YEAR", )), int(os.getenv("PRODUCTION_DAY_OF_END_MONTH", )), int(os.getenv("PRODUCTION_DAY_OF_END_DAY", )), int(os.getenv("PRODUCTION_DAY_OF_END_HOUR", )), tzinfo=TIMEZONE)]
]

AWS = {
    "aws_access_key_id": os.environ.get("PRODUCTION_AWS_ACCESS_KEY_ID"),
    "aws_secret_access_key": os.environ.get("PRODUCTION_AWS_SECRET_ACCESS_KEY"),
    "region_name":  os.environ.get("PRODUCTION_REGION_NAME"),
}
RESUME_BUCKET = os.getenv("PRODUCTION_RESUME_BUCKET", "")
WAIVER_BUCKET = os.getenv("PRODUCTION_WAIVER_BUCKET", "")
VACCINE_BUCKET = os.getenv("PRODUCTION_VACCINE_BUCKET", "")
# Json webtoken
JWT_SECRET = os.getenv("PRODUCTION_JWT_SECRET", "")
JWT_ALGO = os.getenv("PRODUCTION_JWT_ALGO", "")
