import os
from typing import Union
import unittest
from application import app
from pymongo import database, MongoClient

from api.schemas import BoulderFields
from config import CREDS, CREDS_DEV
from tests.tests_config import DB_NAME, WALLS_COLLECTION
from tests.tests_config import TEST_GYM_NAME, TEST_GYM_CODE, TEST_COORDINATES
from tests.tests_config import TEST_WALL_NAME, TEST_WALL_SECTION, TEST_WALL_RADIUS
from utils.utils import set_creds_file


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
    walls_collection = db[WALLS_COLLECTION]
    if walls_collection.find_one({'id': gym_code}, limit = 1) != 0:
        return
    wall_data = {
        'name': gym_name,
        'id': gym_code,
        'coordinates': coordinates
    }
    walls_collection.insert_one(wall_data)

def add_wall(db, gym_code, wall_name, wall_section, wall_radius):
    if f'{gym_code}_walls' in db.list_collection_names():
        return
    gym_collection = db[f'{gym_code}_walls']
    wall_data = {'image': wall_section, 'name': wall_name, 'radius': wall_radius}
    gym_collection.insert_one(wall_data)


class BaseIntegrationTestClass(unittest.TestCase):
    """
    BaseClass for testing
    """

    def setUp(self):
        """
        Set up method that will run before every test
        """
        # connect to testing ddbb and create emptities
        self.db = get_db()
        self.client = app.test_client()
        create_walls_collection(
            self.db, 
            TEST_GYM_NAME,
            TEST_GYM_CODE, 
            TEST_COORDINATES
        )
        add_wall(
            db=self.db, 
            gym_code=TEST_GYM_CODE, 
            wall_name=TEST_WALL_NAME, 
            wall_section=TEST_WALL_SECTION, 
            wall_radius=TEST_WALL_RADIUS
        )

    def tearDown(self):
        """
        Tear down method that will run after every test
        """
        self.db.client.close()


class BoulderCreationTests(BaseIntegrationTestClass):

    def test_get_gyms(self):
        """
        """
        # Given
        # When
        resp = self.client.get('/api/gym/list')
        # Then
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json['gyms'][0]['name'], TEST_GYM_NAME)

    def test_get_walls(self):
        """
        """
        # Given
        # When
        resp = self.client.get(f'/api/gym/{TEST_GYM_CODE}/walls')
        # Then
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json['walls'][0]['image'], TEST_WALL_SECTION)


    def test_create_boulder_success(self):
        """
        """
        # Given
        fields = BoulderFields()
        data = {
            fields.creator: 'test user',
            fields.difficulty: 'green',
            fields.feet: 'free',
            fields.name: 'test',
            fields.notes: "",
            fields.holds: [{'color': '#00ff00', 'x':0 ,'y':0 }]
        }
        # When
        resp = self.client.post(f'/api/boulders/{TEST_GYM_CODE}/{TEST_WALL_SECTION}/create', json=data)
        # Then
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json['created'], True)


if __name__ == '__main__':
    set_creds_file(CREDS_DEV)
    unittest.main()
    set_creds_file(CREDS)
