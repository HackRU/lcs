import cal_announce


def test_get_cal():
    res = cal_announce.google_cal({}, {})
    print(res)
    assert res["statusCode"] == 200


def test_missing_tok():
    real = cal_announce.token_path
    cal_announce.token_path = "./bogus.pickle"
    
    res = cal_announce.google_cal({}, {})
    assert res["statusCode"] == 500
    cal_announce.token_path = real
