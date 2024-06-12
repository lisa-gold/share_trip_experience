from share_trip_experience import app


def test_home_route():
    response = app.test_client().get('/')

    assert response.status_code == 200
    assert 'Welcome!' in response.text


def test_get_registration():
    response = app.test_client().get('/registration')

    assert response.status_code == 200
    assert 'Name' in response.text


def test_post_registration():
    new_user = {
        'name': 'test',
        'password': '123'
    }
    response = app.test_client().post('/registration', data={
        'name': new_user['name'],
        'password': new_user['password']})

    # todo: test validation

    assert response.status_code == 302
