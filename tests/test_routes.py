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
        'password': '1234'
    }
    response = app.test_client().post('/registration', data={
        'name': new_user['name'],
        'password': new_user['password']}, follow_redirects=True)

    # todo: test validation

    user_added = db_test['users'].find_one({"name": now})

    assert 'successfully' in response.text
    assert user_added is not None
    assert user_added['password'] == new_user['password']

    users_number_before = db_test['users'].count_documents({})

    response_failed_unique = app.test_client().post('/registration', data={
        'name': new_user['name'],
        'password': '44444'}, follow_redirects=True)

    users_number_after = db_test['users'].count_documents({})

    assert 'is already registered' in response_failed_unique.text
    assert users_number_before == users_number_after

    db_test['users'].delete_one({"name": now})

    response_failed_password = app.test_client().post('/registration', data={
        'name': 'some_name',
        'password': '123'}, follow_redirects=True)

    assert 'The password is too short' in response_failed_password.text
    assert db_test['users'].find_one({"name": 'some_name'}) is None
