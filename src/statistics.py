from src import util
from src.schemas import ensure_schema, ensure_logged_in_user, ensure_role

@ensure_schema({
    "type": "object",
    "properties": {
        "token": {"type": "string"}
    },
    "required": ["token"],
    "additionalFields": False
})
@ensure_logged_in_user()
@ensure_role([['director']])
def statistics(event, context, user=None): 
    # fetch the collection that stores user data
    user_coll = util.coll('users')

    # do this for registered, rejected, confirmation, coming, not-coming, waitlist, confirmed, checked-in 
    registered = user_coll.count_documents({"registration_status": "registered"})
    rejected = user_coll.count_documents({"registration_status": "rejected"})
    confirmation = user_coll.count_documents({"registration_status": "confirmation"})
    coming = user_coll.count_documents({"registration_status": "coming"})
    not_coming = user_coll.count_documents({"registration_status": "not-coming"})
    waitlist = user_coll.count_documents({"registration_status": "waitlist"})
    confirmed = user_coll.count_documents({"registration_status": "confirmed"})
    checked_in = user_coll.count_documents({"registration_status": "checked-in"})

    return {
        "statusCode": 200,
        "body": {
            "registered": registered,
            "rejected": rejected,
            "confirmation": confirmation,
            "coming": coming,
            "not-coming": not_coming,
            "waitlist": waitlist,
            "confirmed": confirmed,
            "checked-in": checked_in
        },
        "headers": {
            "Content-Type": "application/json"
        }
    }