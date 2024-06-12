import os
from flask import (
    Flask,
    render_template,
    url_for,
    request,
    flash,
    redirect)
from share_trip_experience.db import get_db


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


app.config["DB"] = get_db()


@app.route('/')
def home():
    return render_template('index.html')


@app.get('/registration')
def registration_form():
    return render_template('registration.html')


@app.post('/registration')
def add_user():
    # todo validation (unique, password length, etc.), encryption
    user = {
        'name': request.form['name'],
        'password': request.form['password']
    }
    app.config["DB"]['users'].insert_one(user)
    flash('User is added successfully', 'alert alert-success')
    return redirect(url_for('get_my_trips'), code=302)


@app.get('/my_trips')
def get_my_trips():
    return render_template('my_trips.html')
