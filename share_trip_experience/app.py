import os
from flask import (
    Flask,
    render_template,
    url_for,
    request,
    flash,
    redirect)
from share_trip_experience.db import get_db, validate_new_user
from share_trip_experience.models import User, Trip
from flask_login import (
    LoginManager,
    login_user,
    logout_user,
    current_user)


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


app.config["DB"] = get_db()
login_manager = LoginManager(app)


@login_manager.user_loader
def loader_user(name):
    user = app.config["DB"]['users'].find_one({"name": name})
    if not user:
        return None
    return User(user['name'], user['password'])


@app.route('/')
def home():
    return render_template('index.html')


@app.get('/registration')
def registration_form():
    return render_template('registration.html')


@app.post('/registration')
def add_user():
    # todo encryption
    user = User(request.form['name'], request.form['password'])
    is_validated, message = validate_new_user(app.config["DB"], user)
    if not is_validated:
        flash(message, 'alert alert-danger')
        return render_template('registration.html')
    app.config["DB"]['users'].insert_one(user.__dict__)
    login_user(User(user.name, user.password))
    flash('User is added successfully', 'alert alert-success')
    return redirect(url_for('get_my_trips'), code=302)


@app.get('/login')
def login_form():
    return render_template('login.html')


@app.post('/login')
def login():
    name = request.form['name']
    user = app.config["DB"]['users'].find_one({"name": name})
    if not user:
        flash(f'User {name} is not registered', 'alert alert-danger')
        return render_template('login.html')

    if user['password'] != request.form['password']:
        flash('Incorrect password', 'alert alert-danger')
        return render_template('login.html')

    login_user(User(user['name'], user['password']))
    flash('User logged in successfully', 'alert alert-success')
    return redirect(url_for('get_my_trips'), code=302)


@app.post('/logout')
def logout():
    logout_user()
    flash('User logged out successfully', 'alert alert-success')
    return redirect(url_for('home'), code=302)


@app.get('/my_trips')
def get_my_trips():
    if not current_user.is_authenticated:
        flash('Log in to open the page', 'alert alert-warning')
        return redirect(url_for('login_form'), code=302)
    name = current_user.name
    user = app.config["DB"]['users'].find_one({"name": name})
    trips = user.get('trips') or []
    return render_template('my_trips.html', trips=trips)


@app.post('/my_trips')
def add_trip():
    if not current_user.is_authenticated:
        flash('Log in to open the page', 'alert alert-warning')
        return redirect(url_for('login_form'), code=302)
    places = []
    food = []
    for i in range(1, 11):
        if request.form.get(f'place{i}'):
            places.append(request.form[f'place{i}'])
        if request.form.get(f'food{i}'):
            food.append(request.form[f'food{i}'])

    trip = Trip(
        request.form['country'],
        request.form['city'],
        request.form['year-month'][:4],
        request.form['year-month'][5:],
        places,
        food,
        request.form['rating'],
    )
    user = app.config["DB"]['users'].find_one({"name": current_user.name})
    trips_updated = []
    if user.get('trips'):
        trips_updated = user.get('trips') + [trip.__dict__]
    else:
        trips_updated = [trip.__dict__]
    app.config["DB"]['users'].update_one({"name": current_user.name},
                                         {"$set": {'trips': trips_updated}})
    flash('Your new trip is added successfully', 'alert alert-success')
    return redirect(url_for('get_my_trips'), code=302)


@app.post('/my_trips/<trip_index>/delete')
def delete_trip(trip_index):
    if not current_user.is_authenticated:
        flash('Log in to open the page', 'alert alert-warning')
        return redirect(url_for('login_form'), code=302)
    user = app.config["DB"]['users'].find_one({"name": current_user.name})
    trips_updated = user.get('trips')
    trips_updated.pop(int(trip_index))

    app.config["DB"]['users'].update_one({"name": current_user.name},
                                         {"$set": {'trips': trips_updated}})
    flash('Trip is deleted successfully', 'alert alert-success')
    return redirect(url_for('get_my_trips'), code=302)


@app.get('/my_trips/<trip_index>/edit')
def edit_trip_form(trip_index):
    if not current_user.is_authenticated:
        flash('Log in to open the page', 'alert alert-warning')
        return redirect(url_for('login_form'), code=302)
    user = app.config["DB"]['users'].find_one({"name": current_user.name})
    trip_to_updated = user.get('trips')[int(trip_index)]
    return render_template('edit_trip.html',
                           trip=trip_to_updated,
                           trip_index=trip_index)


@app.post('/my_trips/<trip_index>/edit')
def edit_trip(trip_index):
    if not current_user.is_authenticated:
        flash('Log in to open the page', 'alert alert-warning')
        return redirect(url_for('login_form'), code=302)
    user = app.config["DB"]['users'].find_one({"name": current_user.name})
    trips_updated = user.get('trips')
    trips_updated.pop(int(trip_index))
    places = []
    food = []
    for i in range(1, 11):
        if request.form.get(f'place{i}'):
            places.append(request.form[f'place{i}'])
        if request.form.get(f'food{i}'):
            food.append(request.form[f'food{i}'])

    trip_updated = Trip(
        request.form['country'],
        request.form['city'],
        request.form['year-month'][:4],
        request.form['year-month'][5:],
        places,
        food,
        request.form['rating'],
    )
    trips_updated.insert(int(trip_index), trip_updated.__dict__)

    app.config["DB"]['users'].update_one({"name": current_user.name},
                                         {"$set": {'trips': trips_updated}})
    flash('Trip is edited successfully', 'alert alert-success')
    return redirect(url_for('get_my_trips'), code=302)


@app.get('/users')
def get_users():
    users = app.config["DB"]['users'].find({}).sort("trips", -1)
    return render_template('users.html',
                           users=users)


@app.get('/users/<name>')
def get_user(name):
    user = app.config["DB"]['users'].find_one({"name": name})
    if current_user.is_authenticated and current_user.name == name:
        return render_template('my_trips.html', trips=user.get('trips', []))
    return render_template('users_trips.html',
                           user=user)
