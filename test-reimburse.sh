AUTH=$(curl -H "content-type: application/json" -d "{\"email\": \"a@a.com\", \"password\": \"a\"}" https://7c5l6v7ip3.execute-api.us-west-2.amazonaws.com/lcs-test/authorize \
    | python -c "import json; print(json.loads(json.loads(input())['body'])['auth']['token'])")

curl -H "content-type: application/json" -d "{\"email\": \"a@a.com\", \"token\": \"$AUTH\"}" https://7c5l6v7ip3.execute-api.us-west-2.amazonaws.com/lcs-test/reimburse
