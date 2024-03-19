from src import util
from src.schemas import ensure_schema, ensure_logged_in_user, ensure_role
from src.util import coll
import json

# the request body will require: 
# 1. team_leader: email (string)
# 2. team_members: [strings]

# procedure: 
# 1. Team leader and team members need to be distinct
# 2. check to see if team_leader exists and is teamless (must be true before proceed)
# 3. check to see if ALL team_members exist and are teamless (must be true before proceed)
# 4. create a new team in collection "Team", assign a team_id by: getting the total no. of teams in collection + 1
# 5. Go find each user, including team leader and member, attach team_id into their user profile

@ensure_schema({
    "type": "object",
    "properties": {
        "team_leader": {"type": "string"},
        "team_members": {"type": "array"}
    },
    "required": ["team_leader", "team_members"]
})
def make_teams(event, context):
    team_leader_email = event['team_leader']
    team_members_emails = event['team_members']

    users = coll('users')
    teams = coll('teams')
    
    # Team leader and team members need to be distinct
    if team_leader_email in team_members_emails:
        return {"status": 400, "error": "team leader email is the same as one of the members"}

    # team members (array of strings) need to be distinct among themselves 
    if len(team_members_emails) != len(set(team_members_emails)):
        return {"status": 400, "error": "team member emails need to be distinct"}
    

    # check to see if team leader exists and is teamless 
    team_leader = users.find_one({"email": team_leader_email})

    if team_leader is not None:
        if "team_id" in team_leader and team_leader['team_id'] > 0:
            return {"status": 400, "error": "team leader already has a team"}
    else:
        return {"status": 400, "error": "team leader email does not exist"}
    
    # check to see if all team members exist and are teamless
    for member_email in team_members_emails:
        team_member = users.find_one({"email": member_email})
        if team_member is not None:
            if "team_id" in team_member and team_member['team_id'] > 0:
                return {"status": 400, "error": "team member already has a team"}
        else:
            return {"status": 400, "error": "this team member email does not exist", "email": member_email}
        
    # create a team
    try: 
        teams_count = teams.count_documents({})
        new_team = teams.insert_one({
            "team_leader": team_leader_email,
            "team_members": team_members_emails,
            "team_id":  teams_count + 1
        })

        # assigning team_id to team leader and members in Users collection
        team_id = teams_count + 1
        
        update_team_leader_id = users.find_one_and_update({"email": team_leader_email}, 
                                                        {
                                                            '$set': {'team_id': team_id}
                                                        })
        
        for member_email in team_members_emails:
            update_team_member_id = users.find_one_and_update({"email": member_email}, 
                                                        {
                                                            '$set': {'team_id': team_id}
                                                        })
    except Exception as e:
        return {"status": 500, 'error': e}
    
    # success response
    return {
        "status": 200,
        "body": {
            "team_id": team_id
        }
    }