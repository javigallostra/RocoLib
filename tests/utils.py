import os
from typing import Union
from pymongo import database, MongoClient
from tests.tests_config import DB_NAME, WALLS_COLLECTION


def get_creds(file: str = 'creds_dev.txt') -> Union[str, None]:
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
    wall_data = {'image': wall_section,
                 'name': wall_name, 'radius': wall_radius}
    gym_collection.insert_one(wall_data)


def drop_boulders(db, gym_code):
    """
    Remove any boulder present in the test collection
    """
    boulders_collection = db[f'{gym_code}_boulders']
    boulders_collection.drop()
