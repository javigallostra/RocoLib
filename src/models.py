from __future__ import annotations
from typing import Any, Dict, Union
import uuid

from src.typing import Data
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from db import mongodb_controller
from datetime import datetime
from pymongo.database import Database
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)

TICKLIST = 'ticklist'
USER_PREFERENCES = 'user_preferences'

class UserPreferences:
    """User preferences model"""
    def __init__(self, user_id: str, **kwargs) -> None:
        self.user_id = user_id
        self.default_gym = ""
        for key in kwargs:
            setattr(self, key, kwargs[key])

class User(UserMixin):
    """User model"""

    def __init__(self, *initial_data, **kwargs) -> None:
        """
        Initialise attributes
        """
        self.id: str = None
        self.name: str = None
        self.email: str = None
        self.password: str = None
        self.is_admin: bool = False
        self.user_preferences: UserPreferences = None
        self.ticklist: list[Union[TickListProblem, Data]] = []

        # initial_data is a tuple of args. Here we are
        # assuming that when building a user object a dictionary
        # with all the required data will come as a positional (and the only?)
        # argument
        for arg in initial_data:
            for key in arg:
                if key == TICKLIST:
                    self.load_ticklist(arg[key])
                elif key == USER_PREFERENCES:
                    if isinstance(arg[key], UserPreferences):
                        self.user_preferences = arg[key]
                    else:
                        self.user_preferences = UserPreferences(**arg[key])
                else:
                    setattr(self, key, arg[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def set_password(self, password: str) -> None:
        """
        Set the password for the current user
        """
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        Return True if the password matches the one from the user
        """
        return check_password_hash(self.password, password)

    def save(self, database: Database) -> None:
        """
        Save the current user data to the database
        """
        if not self.id:
            self.id = str(uuid.uuid1())
        # Serialize ticklist problems
        self.ticklist = [problem.serialize() for problem in self.ticklist]
        to_save = self.__dict__
        user_preferences = to_save.pop(USER_PREFERENCES, None)
        mongodb_controller.save_user(to_save, database)
        mongodb_controller.save_user_preferences(user_preferences.__dict__, database)
        # deserialize ticklist problems
        self.load_ticklist(self.ticklist)

    def load_ticklist(self, ticklist_data: list[Data]) -> None:
        """
        Overwrite the ticklist attribute with new TickListProblems
        created using the data given
        """
        self.ticklist = [TickListProblem(problem) for problem in ticklist_data]

    @staticmethod
    def get_user_preferences(user_id: str, database: Database) -> Union[UserPreferences, None]:
        """
        Get the preferences of a user
        """ 
        _user_prefs = mongodb_controller.get_user_preferences(user_id, database)
        if not bool(_user_prefs):
            return UserPreferences(user_id=user_id)
        return UserPreferences(**_user_prefs)

    @staticmethod
    def get_by_id(user_id: str, database: Database) -> Union[User, None]:
        """
        Return a User object if the user id is found in the database.
        
        Otherwise, return None.
        """
        user_data = mongodb_controller.get_user_data_by_id(user_id, database)
        if not bool(user_data):
            return None
        
        user_prefs = UserPreferences(user_id)
        _user_prefs = mongodb_controller.get_user_preferences(user_id, database)        
        if bool(_user_prefs):
            user_prefs = UserPreferences(**_user_prefs)

        user_data[USER_PREFERENCES] = user_prefs

        return User(user_data)

    @staticmethod
    def get_user_by_email(email: str, database: Database) -> Union[User, None]:
        """
        Return a User object if the user email is found in the database.
        Otherwise, return None.
        """
        user_data = mongodb_controller.get_user_data_by_email(email, database)
        if not user_data:
            return None

        user_prefs = UserPreferences(user_data['id'])
        _user_prefs = mongodb_controller.get_user_preferences(user_data['id'], database)        
        if bool(_user_prefs):
            user_prefs = UserPreferences(**_user_prefs)

        user_data[USER_PREFERENCES] = user_prefs

        return User(user_data)

    @staticmethod
    def get_user_by_username(name: str, database: Database) -> Union[User, None]:
        """
        Return a User object if the user email is found in the database.
        Otherwise, return None.
        """
        user_data = mongodb_controller.get_user_data_by_username(name, database)
        if not user_data:
            return None

        user_prefs = UserPreferences(user_data['id'])
        _user_prefs = mongodb_controller.get_user_preferences(user_data['id'], database)        
        if bool(_user_prefs):
            user_prefs = UserPreferences(**_user_prefs)

        user_data[USER_PREFERENCES] = user_prefs

        return User(user_data)

    def generate_auth_token(self, app: Any, expiration: int = 600):
        s = Serializer(app.secret_key, expires_in = expiration)
        return s.dumps({ 'id': self.id })

    @staticmethod
    def verify_auth_token(token: str, app: Any, database: Database) -> User:
        s = Serializer(app.secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None # valid token, but expired
        except BadSignature:
            return None # invalid token
        user_data = mongodb_controller.get_user_data_by_id(data['id'], database)
        if not user_data:
            return None
        return User(user_data)

    def __repr__(self):
        return '<User {} ({})>'.format(self.email, self.name)


class TickListProblem():
    """
    Tick List problem model
    """

    def __init__(self, *initial_data, **kwargs) -> None:
        """
        Initialise attributes
        """
        self.iden: str = None
        self.gym: str = None
        self.section: str = None
        self.is_done: bool = False
        self.date_climbed: str = None
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def tick_problem(self) -> None:
        """
        Set the problem is_done value to True and
        the date_climbed value to the current date
        """
        self.is_done = True
        self.date_climbed = datetime.today().strftime('%Y-%m-%d')

    def serialize(self) -> Dict[str, Any]:
        """
        Return a serialized version of itself (a dictionary)
        """
        return self.__dict__
