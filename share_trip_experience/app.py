import os
from flask import (  # type: ignore
    Flask,
    render_template)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def home():
    return render_template('index.html')
