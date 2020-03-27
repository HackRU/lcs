import requests

import config
import util
from schemas import ensure_schema, ensure_logged_in_user
from util import add_cors_headers


def create_error_response(err_msg: str):
    return add_cors_headers({"statusCode": 503, "body": err_msg})


def process_slack_error(error_str: str):
    if error_str in ["user_not_found", "user_not_visible", "user_disabled"]:
        return add_cors_headers(
                {"statusCode": 403, "body": f"There was an error with the user id's provided: {error_str}"})
    else:
        return create_error_response(f"Encountered a slack API error: {error_str}")


@ensure_schema({
    "type": "object",
    "properties": {
        "email": {"type": "string", "format": "email"},
        "token": {"type": "string"},
        "other_email": {"type": "string", "format": "email"}
    },
    "required": ["email", "token", "other_email"]
})
@ensure_logged_in_user()
def generate_dm_link(event, context, user):
    other_user = util.coll("users").find_one({"email": event["other_email"]})
    if other_user is None:
        return add_cors_headers({"statusCode": 403, "body": "Other user not found within LCS"})
    if "token" not in config.SLACK_KEYS or not config.SLACK_KEYS["token"]:
        return create_error_response("Slack API token not configured")
    this_slack_id = user.get("slack_id", None)
    other_slack_id = other_user.get("slack_id", None)
    if this_slack_id is None or other_slack_id is None:
        return add_cors_headers({"statusCode": 403, "body": "Slack ID not present within LCS for the given user(s)"})
    api_link = r"https://slack.com/api/conversations.open"
    slack_api_payload = {"token": config.SLACK_KEYS["token"], "users": f"{this_slack_id},{other_slack_id}"}
    slack_api_headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url=api_link, data=slack_api_payload, headers=slack_api_headers)
    if response.status_code != requests.codes.OK:
        return create_error_response("Encountered a Slack API error")
    response_json = response.json()
    was_successful = response_json["ok"]
    if not was_successful:
        return process_slack_error(response_json["error"])
    creation_info = response_json["channel"]
    dm_id = creation_info["id"]
    server_id = creation_info["shared_team_ids"][0]
    link_to_dm = rf"https://apps.slack.com/client/{server_id}/{dm_id}"
    return add_cors_headers({"statusCode": 200, "body": {"slack_dm_link": link_to_dm}})
