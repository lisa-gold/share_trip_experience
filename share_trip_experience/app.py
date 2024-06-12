import os
from dotenv import load_dotenv
from flask import (
    Flask,
    render_template,
    url_for,
    request,
    flash,
    redirect)
from pymongo import MongoClient


load_dotenv()


USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
DB = os.getenv("DB")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


try:
    # todo: test mode
    cluster = MongoClient(f"mongodb+srv://{USERNAME}:{PASSWORD}@{DB}")
    db = cluster['trip-share']
except Exception as e:
    print('no connection with the db ', e)


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
    db['users'].insert_one(user)
    flash('User is added successfully', 'alert alert-success')
    return redirect(url_for('get_my_trips'), code=302)


@app.get('/my_trips')
def get_my_trips():
    return render_template('my_trips.html')
