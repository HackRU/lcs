AUTH=$(curl -H "content-type: application/json" -d "{\"email\": \"$1\", \"password\": \"$2\"}" https://m7cwj1fy7c.execute-api.us-west-2.amazonaws.com/mlhtest/authorize \
    | python -c "import json; print(json.loads(json.loads(input())['body'])['auth']['token'])")

echo $AUTH

curl -H "content-type: application/json" -d "{\"email\": \"$1\", \"token\": \"$AUTH\"}" https://m7cwj1fy7c.execute-api.us-west-2.amazonaws.com/mlhtest/reimburse
