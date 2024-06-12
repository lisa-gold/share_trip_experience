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
