from testing_utils import *

from src import cal_announce
from unittest.mock import patch
from config import GOOGLE_CAL
import json


def test_get_cal():
    res = cal_announce.google_cal({'body': json.dumps({})}, {})
    assert res["statusCode"] == 200


@patch.object(GOOGLE_CAL, 'CAL_API_KEY', '')
def test_missing_key():
    res = cal_announce.google_cal({'body': json.dumps({})}, {})
    assert res["statusCode"] == 500


@patch.object(GOOGLE_CAL, 'CAL_API_KEY', 'bad key')
def test_bad_key():
    res = cal_announce.google_cal({'body': json.dumps({})}, {})
    assert res["statusCode"] == 500


@patch.object(GOOGLE_CAL, 'CAL_ID', '')
def test_missing_cal_id():
    res = cal_announce.google_cal({'body': json.dumps({})}, {})
    assert res["statusCode"] == 500


@patch.object(GOOGLE_CAL, 'CAL_ID', 'bad cal id')
def test_bad_cal_id():
    res = cal_announce.google_cal({'body': json.dumps({})}, {})
    assert res["statusCode"] == 500
