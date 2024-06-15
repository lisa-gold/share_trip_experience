import os
from flask import (
    Flask,
    render_template,
    url_for,
    request,
    flash,
    redirect)
from share_trip_experience.db import get_db, validate_new_user
from share_trip_experience.models import User
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
