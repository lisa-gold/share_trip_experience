from flask_login import UserMixin


class User(UserMixin):

    def __init__(self, name, password):
        self.name = name
        self.password = password

    def get_id(self):
        return self.name

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active():
        return True


class Trip():

    def __init__(self, country, city, year, month, places, food, rating):
        self.country = country
        self.city = city
        self.year = year
        self.month = month
        self.places = places
        self.food = food
        self.rating = rating
