from share_trip_experience import app
from share_trip_experience.db import get_db
from share_trip_experience.models import User
import datetime


def test_home_route():
    response = app.test_client().get('/')

    assert response.status_code == 200
    assert 'Welcome!' in response.text


def test_get_registration():
    response = app.test_client().get('/registration')

    assert response.status_code == 200
    assert 'Sign up' in response.text


def test_post_registration():
    now = str(datetime.datetime.now().timestamp())
    db_test = get_db(test_mode=True)
    app.config.update({"TESTING": True, "DB": db_test})
    new_user = User(now, '1234')
    response = app.test_client().post('/registration', data={
        'name': new_user.name,
        'password': new_user.password}, follow_redirects=True)

    user_added = db_test['users'].find_one({"name": now})

    assert 'successfully' in response.text
    assert user_added is not None
    assert user_added['password'] == new_user.password

    users_number_before = db_test['users'].count_documents({})

    response_failed_unique = app.test_client().post('/registration', data={
        'name': new_user.name,
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


def test_get_login():
    response = app.test_client().get('/login')

    assert response.status_code == 200
    assert 'Sign in' in response.text


def test_post_login():
    db_test = get_db(test_mode=True)
    user_existing = db_test['users'].find_one({"name": '1718441680.747165'})
    response = app.test_client().post('/login', data={
        'name': user_existing['name'],
        'password': user_existing['password']}, follow_redirects=True)

    assert 'User logged in successfully' in response.text

    response_wrong_password = app.test_client().post('/login', data={
        'name': user_existing['name'],
        'password': '1111'}, follow_redirects=True)

    assert 'Incorrect password' in response_wrong_password.text

    response_unregistered_user = app.test_client().post('/login', data={
        'name': 'new_name',
        'password': '1111'}, follow_redirects=True)

    assert 'is not registered' in response_unregistered_user.text


def test_logout():
    response = app.test_client().post('/logout', follow_redirects=True)
    assert 'User logged out successfully' in response.text


def test_get_my_trips():
    app.test_client().post('/logout')
    response_error = app.test_client().get('/my_trips', follow_redirects=True)
    assert 'Log in to open the page' in response_error.text

    db_test = get_db(test_mode=True)
    user_existing = db_test['users'].find_one({"name": '1718441680.747165'})
    with app.test_client() as client:
        client.post('/login',
                    data={'name': user_existing['name'],
                          'password': user_existing['password']},
                    follow_redirects=True)
        response = client.get('/my_trips')

        assert response.status_code == 200
        assert 'My trips' in response.text
        assert 'Japan' in response.text


def test_post_my_trips():
    app.test_client().post('/logout')
    response_error = app.test_client().post('/my_trips', follow_redirects=True)
    assert 'Log in to open the page' in response_error.text

    db_test = get_db(test_mode=True)
    user_existing = db_test['users'].find_one({"name": '1718441680.747165'})
    with app.test_client() as client:
        client.post('/login',
                    data={'name': user_existing['name'],
                          'password': user_existing['password']},
                    follow_redirects=True)

        old_trips = db_test['users'].find_one({
            "name": user_existing['name']}).get('trips')

        response = client.post('/my_trips',
                               data={'country': 'Madagascar',
                                     'city': 'Antananarivo',
                                     'year-month': '2024-01',
                                     'rating': 6},
                               follow_redirects=True)

        assert 'Madagascar' in response.text

        db_test['users'].update_one({"name": user_existing['name']},
                                    {"$set": {'trips': old_trips}})


def test_delete_trip():
    app.test_client().post('/logout')
    response_error = app.test_client().post('/my_trips', follow_redirects=True)
    assert 'Log in to open the page' in response_error.text

    db_test = get_db(test_mode=True)
    user_existing = db_test['users'].find_one({"name": '1718441680.747165'})
    with app.test_client() as client:
        client.post('/login',
                    data={'name': user_existing['name'],
                          'password': user_existing['password']},
                    follow_redirects=True)

        trip_to_delete = {'country': 'Madagascar',
                          'city': 'Antananarivo',
                          'year-month': '2024-01',
                          'rating': 6}

        # add trip that will be deleted
        client.post('/my_trips',
                    data=trip_to_delete,
                    follow_redirects=True)

        existing_trips = db_test['users'].find_one({
            "name": user_existing['name']}).get('trips')

        number_of_trips = len(existing_trips)  # 2

        response = client.post(f'/my_trips/{number_of_trips - 1}/delete',
                               follow_redirects=True)

        existing_trips_after = db_test['users'].find_one({
            "name": user_existing['name']}).get('trips')

        number_of_trips_after = len(existing_trips_after)

        assert 'Trip is deleted successfully' in response.text
        assert number_of_trips_after == number_of_trips - 1
        assert existing_trips[:-1] == existing_trips_after
