import uuid 
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from db import firebase_controller

class User(UserMixin):

    # def __init__(self, id, name, email, password, is_admin=False):
    def __init__(self, *initial_data, **kwargs):
        self.id = None
        self.name = None
        self.email = None
        self.password = None
        self.is_admin = False

        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def save(self):
        # TODO: check if user already exists
        if not self.id:
            self.id = str(uuid.uuid1())
        firebase_controller.save_user(self.__dict__)

    @staticmethod
    def get_by_id(user_id):
        user_data = firebase_controller.get_user_data_by_id(user_id)
        if not user_data:
            return None 
        return User(user_data)

    @staticmethod
    def get_user_by_email(email):
        user_data = firebase_controller.get_user_data_by_email(email=email)
        if not user_data:
            return None 
        return User(user_data)

    def __repr__(self):
        return '<User {}>'.format(self.email)

# For testing purposes
users = []

def get_user(email):
    for user in users:
        if user.email == email:
            return user
    return None

if __name__ == '__main__':
    test_user = User(1, "test", "test@test.com", "pass", is_admin=False)
    test_user.save()