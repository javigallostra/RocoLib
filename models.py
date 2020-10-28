from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from db import firebase_controller

class User(UserMixin):

    def __init__(self, id, name, email, password, is_admin=False):
        self.id = id
        self.name = name
        self.email = email
        self.password = generate_password_hash(password)
        self.is_admin = is_admin

    def set_password(self, password):
        self.password = generate_password_hash(password)


    def check_password(self, password):
        return check_password_hash(self.password, password)

    def save(self):
        # TODO: check if user already exists
        firebase_controller.save_user(self.__dict__)

    @staticmethod
    def get_by_id(id):
        return firebase_controller.get_user_by_id(id)

    @staticmethod
    def get_by_email(email):
        return firebase_controller.get_user_by_email(email=email).first()

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