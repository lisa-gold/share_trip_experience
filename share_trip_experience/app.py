import os
from flask import (
    Flask,
    render_template,
    url_for,
    request,
    flash,
    redirect)
from share_trip_experience.db import get_db, validate_new_user


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
    # todo encryption
    user = {
        'name': request.form['name'],
        'password': request.form['password']
    }
    is_validated, message = validate_new_user(app.config["DB"], user)
    if not is_validated:
        flash(message, 'alert alert-danger')
        return render_template('registration.html')
    app.config["DB"]['users'].insert_one(user)
    flash('User is added successfully', 'alert alert-success')
    return redirect(url_for('get_my_trips'), code=302)


@app.get('/my_trips')
def get_my_trips():
    return render_template('my_trips.html')
