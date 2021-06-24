import uuid 
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from db import mongodb_controller
from datetime import datetime

TICKLIST = "ticklist"

# Boulder constants
BOULDER_COLOR_MAP = {
    'green': '#2CC990',
    'blue': '#2C82C9',
    'yellow': '#EEE657',
    'red': '#FC6042'
}

# Mappings of DB feet field values to friendly text to render
FEET_MAPPINGS = {
    'free': 'Free feet',
    'follow': 'Feet follow hands',
    'no-feet': 'Campus',
}

class User(UserMixin):
    """
    User model
    """
    def __init__(self, *initial_data, **kwargs):
        self.id = None
        self.name = None
        self.email = None
        self.password = None
        self.is_admin = False
        self.ticklist = []

        for dictionary in initial_data:
            for key in dictionary:
                if key == TICKLIST:
                    self.load_ticklist(dictionary[key])
                else:
                    setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def save(self, database):
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
    def get_by_id(user_id, database):
        user_data = mongodb_controller.get_user_data_by_id(user_id, database)
        if not user_data:
            return None
        return User(user_data)

    @staticmethod
    def get_user_by_email(email, database):
        user_data = mongodb_controller.get_user_data_by_email(email, database)
        if not user_data:
            return None 
        return User(user_data)

    def __repr__(self):
        return '<User {}>'.format(self.email)

class BoulderProblem():
    """
    Boulder problem Model
    """
    def __init__(self, db, gym, *initial_data, **kwargs) -> None:
        # Boulder values coming from DDBB
        self._id = None
        self.rating = None
        self.raters = None
        self.name = None
        self.creator = None
        self.difficulty = None
        self.feet = None
        self.holds = None
        self.section = None
        self.time = None
        # fields to serialize
        self.to_serialize = tuple(key for d in initial_data for key in d)
        for dictionary in initial_data:
            for key in dictionary:
                setattr(self, key, dictionary[key])
        for key in kwargs:
            setattr(self, key, kwargs[key])
        # additional values
        self.is_done = False
        self.safe_name = secure_filename(self.name)
        self.color = self.map_difficulty_to_color(self.difficulty)
        self.radius = mongodb_controller.get_walls_radius_all(db)[gym + '/' + self.section]

    def get_id(self) -> str:
        return self._id

    def map_feet(self, feet) -> str:
        return FEET_MAPPINGS[feet]

    def map_difficulty_to_color(self, difficulty) -> str:
        return BOULDER_COLOR_MAP[difficulty]

    def map_values(self) -> None:
        self.difficulty = self.map_difficulty(self.difficulty)
        self.feet = self.map_feet(self.feet)
    
    def map_values_for_db(self):
        pass

    def serialize_all(self) -> dict:
        data = self.__dict__
        data.pop('to_serialize', False)
        return data

    def serialize_for_db(self) -> dict:
        return {key: self.__dict__[key] for key in self.__dict__ if key in self.to_serialize} 

class TickListProblem():
    """
    Tick List problem model
    """
    def __init__(self, *initial_data, **kwargs):
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

    def tick_problem(self):
        self.is_done = True
        self.date_climbed = datetime.today().strftime('%Y-%m-%d')
    
    def serialize(self):
        return self.__dict__
