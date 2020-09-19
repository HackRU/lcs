LCS_URL="https://7c5l6v7ip3.execute-api.us-west-2.amazonaws.com/lcs-test"
if [ $# -eq 3 ]
then
    LCS_URL="https://m7cwj1fy7c.execute-api.us-west-2.amazonaws.com/mlhtest"
fi

AUTH=$(curl -H "content-type: application/json" -d "{\"email\": \"$1\", \"password\": \"$2\"}" "$LCS_URL/authorize" \
    | python -c "import json; print(json.loads(json.loads(input())['body'])['auth']['token'])")

echo $AUTH

curl -H "content-type: application/json" -d "{\"email\": \"$1\", \"token\": \"$AUTH\"}" "$LCS_URL/reimburse"
