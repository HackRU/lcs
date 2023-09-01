from testing_utils import *
from src import statistics, authorize
import pytest

# @pytest.mark.run(order=1)
# def test_when_director_logs_in(): # success case
#     user_email = "director@test"
#     password = "director"
#     usr_dict = {"email": user_email, "password": password}
#     auth = authorize.authorize(usr_dict, None)

#     auth_token = auth['body']['token']

#     # make sure user exists
#     user_dict = get_db_user(user_email)
#     assert 'email' in user_dict and user_dict['email'] == user_email

#     # make call 
#     success = statistics.statistics({'token': auth_token}, None)
#     expected_schema = {
#         "type": "object",
#         "properties": {
#             "registered": {"type": "integer"},
#             "rejected": {"type": "integer"},
#             "confirmation": {"type": "integer"},
#             "coming": {"type": "integer"},
#             "not-coming": {"type": "integer"},
#             "waitlist": {"type": "integer"},
#             "confirmed": {"type": "integer"},
#             "checked-in": {"type": "integer"}
#         },
#         "required": ['registered', "rejected", "confirmation", "coming", "not-coming", "waitlist", "confirmed", "checked-in"]
#     }
#     assert check_by_schema(schema_for_http(200, expected_schema), success)

@pytest.mark.run(order=2)
def test_when_non_director_logs_in(): # failure case
    user_email = "creep@radiohead.ed" # this user is a hacker, not director
    password = 'love'
    usr_dict = {"email": user_email, "password": password}
    auth = authorize.authorize(usr_dict, None)

    auth_token = auth['body']['token']

    # make sure user exists
    user_dict = get_db_user(user_email)
    assert 'email' in user_dict and user_dict['email'] == user_email

    # make call
    failure = statistics.statistics({"token": auth_token}, None)
    assert check_by_schema(schema_for_http(403, {"type": "string", "const": "User does not have privileges."}), failure)
