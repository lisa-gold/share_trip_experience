from share_trip_experience import app
from share_trip_experience.db import get_db
import datetime


def test_home_route():
    response = app.test_client().get('/')

    assert response.status_code == 200
    assert 'Welcome!' in response.text


def test_get_registration():
    response = app.test_client().get('/registration')

    assert response.status_code == 200
    assert 'Name' in response.text


def test_post_registration():
    now = str(datetime.datetime.now().timestamp())
    db_test = get_db(test_mode=True)
    app.config.update({"TESTING": True, "DB": db_test})
    new_user = {
        'name': now,
        'password': '123'
    }
    response = app.test_client().post('/registration', data={
        'name': new_user['name'],
        'password': new_user['password']}, follow_redirects=True)

    # todo: test validation

    user_added = db_test['users'].find_one({"name": now})

    assert 'successfully' in response.text
    assert user_added is not None
    assert user_added['password'] == new_user['password']

    db_test['users'].delete_one({"name": now})
