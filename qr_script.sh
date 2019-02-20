#!/usr/bin/env bash
# run with `chromium $(./qr_script.sh test@example.com)`
email='test@example.com'
if test $# -ge 1
then
	email=$1
fi
curl -H "content-type: application/json" -d "{\"email\": \"$email\", \"color\": [0,0,0], \"background\": [255,255,255]}" https://m7cwj1fy7c.execute-api.us-west-2.amazonaws.com/test/qr | grep -o 'data.*",' | sed 's/..$//'
# curl -H "content-type: application/json" -d "{\"email\": \"$email\", \"color\": [0,0,0], \"background\": [255,255,255]}" https://https://7c5l6v7ip3.execute-api.us-west-2.amazonaws.com/lcs-test/qr | grep -o 'data.*",' | sed 's/..$//'
