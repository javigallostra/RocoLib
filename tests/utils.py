import os
import bson
from typing import Union
from pymongo import database, MongoClient
from models import User
from tests.tests_config import DB_NAME, WALLS_COLLECTION
import ticklist_handler
from tests.tests_config import TEST_GYM_CODE, TEST_NAME, TEST_WALL_SECTION, TEST_USERNAME
import db.mongodb_controller as mongodb_controller

class FakeRequest:
    def __init__(self, db):
        self.data = None
        self.form = None
        self.json = {
        'gym': TEST_GYM_CODE,
        'name': TEST_NAME,
        'iden':
            mongodb_controller.get_boulder_by_name(
                TEST_GYM_CODE,
                TEST_NAME,
                db
        ).get('_id', ''),
        'is_done': True,
        'section': TEST_WALL_SECTION
        }

    def get_data(self):
        return None


def get_creds(file: str = 'creds.local.txt') -> Union[str, None]:
    """
    Get DDBB credentials
    """
    creds = None
    if os.path.isfile(file):
        with open(file, 'r') as f:
            creds = f.readline()
    return creds


def get_db() -> database.Database:
    """
    Opens a new database connection if there is none yet for the
    current application context.
    """
    client = MongoClient(
        get_creds(),
        connectTimeoutMS=30000,
        socketTimeoutMS=None,
        # socketKeepAlive=True,
        connect=False,
        maxPoolsize=1)
    return client[DB_NAME]


def create_walls_collection(db, gym_name, gym_code, coordinates):
    """
    Add a test gym to the database if it doesn't exist
    """
    walls_collection = db[WALLS_COLLECTION]
    if walls_collection.find_one({'id': gym_code}, limit=1) != 0:
        return
    wall_data = {
        'name': gym_name,
        'id': gym_code,
        'coordinates': coordinates
    }
    walls_collection.insert_one(wall_data)


def add_wall(db, gym_code, wall_name, wall_section, wall_radius):
    """
    Add a test wall linked to the test gym if it doesn't exist
    """
    if f'{gym_code}_walls' in db.list_collection_names():
        return
    gym_collection = db[f'{gym_code}_walls']
    wall_data = {
        'image': wall_section,
        'name': wall_name, 
        'radius': wall_radius,
        'latest': True
    }
    gym_collection.insert_one(wall_data)


def drop_boulders(db, gym_code):
    """
    Remove any boulder present in the test collection
    """
    boulders_collection = db[f'{gym_code}_boulders']
    boulders_collection.drop()


def drop_users(db):
    """
    Remove users from the database
    """
    users_collection = db[f'users']
    users_collection.drop()

def add_boulder(db, gym, boulder_data):
    boulder_data['_id'] = str(bson.objectid.ObjectId())
    result = db[f'{gym}_boulders'].insert_one(boulder_data)
    if result is not None:
        return result.inserted_id


def add_user_with_ticklist(db, username, password, email):
    """
    Add a user to the database
    """
    user = User(name=username, email=email)
    user.set_password(password)
    user.save(db)
    # Boulder comes in the Fake Request
    ticklist_handler.add_boulder_to_ticklist(FakeRequest(db), User().get_user_by_username(TEST_USERNAME, db), db, mark_as_done_clicked=True)

