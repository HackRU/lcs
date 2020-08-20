import datetime
import logging

import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging

from cal_announce import slack_announce, google_cal
from config import FIREBASE

logger = logging.getLogger()
logger.setLevel(logging.INFO)

firebase_admin.initialize_app(credentials.Certificate(FIREBASE.CREDENTIALS))

def send_notification(topic, content):
    """Sends a notification to the appropriate topic in Firebase.

    Documentation:
    https://firebase.google.com/docs/cloud-messaging/manage-topics
    https://firebase.google.com/docs/cloud-messaging/send-message#send-messages-to-topics
    https://firebase.google.com/docs/reference/admin/python/firebase_admin.messaging.html
    https://firebase.google.com/docs/reference/fcm/rest/v1/ErrorCode
    """
    message = messaging.Message(topic=topic, data=content)
    return messaging.send(message)

def check_slack(n=10):
    """Retrieves latest message from slack. If the message timestamp is within n minutes of the
    current time, returns the message body.
    """
    slack_resp = slack_announce({"num_messages": 1}, None)
    if slack_resp["statusCode"] != 200:
        return {"error": f'Error retriving slack messages: {slack_resp["statusCode"]} {slack_resp["body"]}'}

    latest_msg = slack_resp["body"][0]
    msg_time = datetime.datetime.utcfromtimestamp(float(latest_msg["ts"]))
    if msg_time + datetime.timedelta(minutes=n) > datetime.datetime.utcnow():
        body = latest_msg["text"]
    return {"body": body}

def slack_notifications():
    """Cron job to send Firebase notifications whenever a new Slack message appears in #announcements."""
    slack_msg = check_slack()

    if "error" in slack_msg:
        logging.error(slack_msg["error"])
        return

    if not slack_msg["body"]:
        logging.info("No new slack messages")
        return

    try:
        response = send_notification(topic, {"body": slack_msg["body"]})
        logging.info(f"Firebase message sent successfully! Response: {response}")
    except Exception as e:
        logging.error(f"Firebase messaging error: {e}")

def check_google_calendar(n=10):
    """WIP - Retrieves latest event from Google Calendar. If the event timestamp is within n minutes of the
    current time, returns the event body.
    """
    cal_resp = google_cal({"num_events": 1}, None)
    if cal_resp["statusCode"] != 200:
        return {"error": f'Error retriving Google Calendar events: {cal_resp["statusCode"]} {cal_resp["body"]}'}

    # TODO: Check time of latest calendar event and make sure it is within bounds (need to get format of cal_resp)

    return {"body": cal_resp["body"]} # Placeholder

def google_calendar_notifications():
    """Cron job to send Firebase notifications whenever a new Google calendar event is approaching."""
    google_cal_event = check_google_calendar()

    if "error" in google_cal_event:
        logging.error(google_cal_event["error"])
        return

    if not google_cal_event["body"]:
        logging.info("No new Google Calendar events")
        return

    try:
        response = send_notification(topic, {"body": google_cal_event["body"]})
        logging.info(f"Firebase message sent successfully! Response: {response}")
    except Exception as e:
        logging.error(f"Firebase messaging error: {e}")

def main():
    """This function should be run as a cron job."""
    slack_notifications()
    google_calendar_notifications()
