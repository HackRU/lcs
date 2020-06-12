import requests
import json

from datetime import datetime, timedelta, timezone

URL = "http://localhost:3000"

"""
    test3@test.com
    password: password
"""

def main():
    # attempt to create a user
    userdata = {'email': 'test4@test.com', "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6InRlc3Q0QHRlc3QuY29tIiwiZXhwIjoxNTkxNTY3OTEwfQ.W25UyOS2M5Fc4kA9bbYEwhaLOJwlTh0W-GJszJextIk"}
    resp = requests.post(URL + '/validate', json=json.dumps(userdata))
    if resp.status_code == 200:
        print("200 OK")
        print(resp.json())
    else:
        print(f'Error: Status code {resp.status_code}')

if __name__=="__main__":
    main()
