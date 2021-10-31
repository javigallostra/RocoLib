from __future__ import annotations
from typing import Any, Optional, Union
import uuid
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from db import mongodb_controller
from datetime import datetime
from pymongo.database import Database

TICKLIST = "ticklist"


class User(UserMixin):
    """
    User model
    """

    def __init__(self, *initial_data, **kwargs) -> None:
        self.id = None
        self.name = None
        self.email = None
        self.password: str = None
        self.is_admin: bool = False
        self.ticklist: list = []

        for dictionary in initial_data:
            for key in dictionary:
                if key == TICKLIST:
                    self.load_ticklist(dictionary[key])
                else:
                    setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def set_password(self, password: str) -> None:
        self.password = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def save(self, database: Database) -> None:
        if not self.id:
            self.id = str(uuid.uuid1())
        # Serialize ticklist problems
        self.ticklist = [problem.serialize() for problem in self.ticklist]
        mongodb_controller.save_user(self.__dict__, database)
        # deserialize ticklist problems
        self.load_ticklist(self.ticklist)

    def load_ticklist(self, ticklist_data):
        self.ticklist = [TickListProblem(problem) for problem in ticklist_data]

    @staticmethod
    def get_by_id(user_id, database: Database) -> Union[User, None]:
        user_data = mongodb_controller.get_user_data_by_id(user_id, database)
        if not user_data:
            return None
        return User(user_data)

    @staticmethod
    def get_user_by_email(email, database: Database) -> Union[User, None]:
        user_data = mongodb_controller.get_user_data_by_email(email, database)
        if not user_data:
            return None
        return User(user_data)

    def __repr__(self):
        return '<User {}>'.format(self.email)


class TickListProblem():
    """
    Tick List problem model
    """

    def __init__(self, *initial_data, **kwargs) -> None:
        self.iden = None
        self.gym = None
        self.section = None
        self.is_done = False
        self.date_climbed = None
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def tick_problem(self) -> None:
        self.is_done = True
        self.date_climbed = datetime.today().strftime('%Y-%m-%d')

    def serialize(self) -> dict[str, Any]:
        return self.__dict__
