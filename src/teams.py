from src import util
from src.schemas import ensure_schema, ensure_logged_in_user, ensure_role
from src.util import coll
import json

# the request body will include: 
# 1. token (for auth)
# 2. team_leader: email (string)
# 3. team_members: [strings]

# procedure: 
# 1. check to see if team_leader is teamless (must be true before proceed)
# 2. check to see if ALL team_members are teamless (must be true before proceed)
# 3. create a new team in collection "Team", assign a team_id by: getting the total no. of teams in collection + 1
# 4. assign team leader and team_members inside Team object (maybe?)
# 5. Go find each user, including team leader and member, attach team_id into their user profile

@ensure_schema({
    "type": "object",
    "properties": {
        "token": {"type": "string"},
        "team_leader": {"type": "string"},
        "team_members": {"type": "array"}
    },
    "required": ["token", "team_leader", "team_members"]
})
def make_teams(event, context):
    team_leader_email = event['team_leader']
    team_members_emails = event['team_members']

    users = coll('users')
    teams = coll('teams')
    
    # check to see if team leader is teamless (consider changing to checking from teams instead of using users)
    team_leader = users.find_one({"email": team_leader_email})

    if "team_id" in team_leader and team_leader['team_id'] > 0:
        return {"status": 400, "body": "team leader already has a team"}
    
    # check to see if all team members are teamless
    for member_email in team_members_emails:
        team_member = users.find_one({"email": member_email})
        if "team_id" in team_member and team_member['team_id'] > 0:
            return {"status": 400, "bodys": "team member already has a team"}
        
    # create a team
    teams_count = teams.count_documents({})
    new_team = teams.insert_one({
        "team_leader": team_leader_email,
        "team_members": team_members_emails,
        "team_id":  teams_count + 1
    })

    # assigning team_id to team leader and members in Users collection
    team_id = teams_count + 1
    print(team_id)
    update_team_leader_id = users.find_one_and_update({"email": team_leader_email}, 
                                                      {
                                                          '$set': {'team_id': team_id}
                                                      })
    
    for member_email in team_members_emails:
        update_team_member_id = users.find_one_and_update({"email": member_email}, 
                                                      {
                                                          '$set': {'team_id': team_id}
                                                      })
    
    return {
        "status": 200,
        "body": {
            "team_id": team_id
        }
    }