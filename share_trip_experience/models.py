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
