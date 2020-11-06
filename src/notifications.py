import datetime
import logging

import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging

from src import cal_announce
from config import FIREBASE

logger = logging.getLogger()
logger.setLevel(logging.INFO)

firebase_admin.initialize_app(credentials.Certificate(FIREBASE.CREDENTIALS))

def send_notification(message_title, message_body, message_topic):
    """Sends a notification to the appropriate topic in Firebase.

    Sends a message consisting of a title and a body in the form of a push
    notification to the Flutter mobile app.

    Documentation:
    https://pub.dev/packages/firebase_messaging
    """
    message = messaging.Message(
        notification=messaging.Notification(
            title=message_title,
            body=message_body,
        ),
        topic=message_topic,
        data={
            "title": message_title,
            "body": message_body,
            "click_action": "FLUTTER_NOTIFICATION_CLICK"
        }
    )
    return messaging.send(message)

def check_slack(n=10):
    """Retrieves latest message from slack. If the message timestamp is within n minutes of the
    current time, returns the message body.
    """
    slack_resp = cal_announce.slack_announce({"num_messages": 1}, None)
    if slack_resp["statusCode"] != 200:
        return {"error": f'Error retriving slack messages: {slack_resp["statusCode"]} {slack_resp["body"]}'}

    if not slack_resp["body"]:
        return {"body": None}

    latest_msg = slack_resp["body"][0]
    msg_time = datetime.datetime.utcfromtimestamp(float(latest_msg["ts"]))
    body = None
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
        response = send_notification("New Slack Announcement!", slack_msg["body"], FIREBASE.TOPIC)
        logging.info(f'Firebase message for Slack ({slack_msg["body"]}) sent successfully! Response: {response}')
    except Exception as e:
        logging.error(f"Firebase messaging error: {e}")

def check_google_calendar(n=10):
    """Retrieves latest event from Google Calendar. If the event timestamp is within n minutes of the
    current time, returns the event body.
    """
    cal_resp = cal_announce.google_cal({"num_events": 1}, None)
    if cal_resp["statusCode"] != 200:
        return {"error": f'Error retriving Google Calendar events: {cal_resp["statusCode"]} {cal_resp["body"]}'}

    if not cal_resp["body"]:
        return {"body": None}

    latest_cal_event = cal_resp["body"][0]
    event_time = datetime.datetime.strptime(latest_cal_event["start"]["dateTime"], "%Y-%m-%dT%H:%M:%S%z")
    body = None
    if datetime.datetime.now(event_time.tzinfo) + datetime.timedelta(minutes=n) > event_time:
        body = latest_cal_event["summary"]
    return {"body": body}

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
        response = send_notification("Calender Event Approaching!", google_cal_event["body"], FIREBASE.TOPIC)
        logging.info(f'Firebase message for Google Calendar ({google_cal_event["body"]}) sent successfully! Response: {response}')
    except Exception as e:
        logging.error(f"Firebase messaging error: {e}")

def main():
    """This function should be run as a cron job."""
    slack_notifications()
    google_calendar_notifications()
