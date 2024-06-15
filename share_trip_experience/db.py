import os
from dotenv import load_dotenv
from pymongo import MongoClient


load_dotenv()


USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
DB = os.getenv("DB")


def get_db(test_mode=False):
    try:
        cluster = MongoClient(f"mongodb+srv://{USERNAME}:{PASSWORD}@{DB}")
        if test_mode:
            db = cluster['trip-test']
        else:
            db = cluster['trip-share']
        return db
    except Exception as e:
        print('no connection with the db ', e)


def validate_new_user(db, user):
    is_validated = True
    message = ''
    if db['users'].find_one({"name": user.name}):
        message = f'This user ({user.name}) is already registered'
        is_validated = False
    if len(user.password) < 4:
        message = 'The password is too short.\
            It has to be at least 4 characters'
        is_validated = False
    return is_validated, message
