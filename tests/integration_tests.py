import unittest
from application import app

from api.schemas import BoulderFields
from config import CREDS, CREDS_DEV
from tests.tests_config import TEST_GYM_NAME, TEST_GYM_CODE, TEST_COORDINATES
from tests.tests_config import TEST_WALL_NAME, TEST_WALL_SECTION, TEST_WALL_RADIUS
from utils.utils import set_creds_file
from tests.utils import get_db, create_walls_collection, add_wall, drop_boulders


class BaseIntegrationTestClass(unittest.TestCase):
    """
    Base Class for integration tests. Connects to DDBB and creates
    required entities
    """

    def setUp(self):
        """
        Set up method that will run before every test
        """
        set_creds_file(
            CREDS_DEV)  # set development credentials for the application
        # connect to testing ddbb and create entities
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
        drop_boulders(self.db, TEST_GYM_CODE)

    def tearDown(self):
        """
        Tear down method that will run after every test
        """
        set_creds_file(CREDS)
        self.db.client.close()


class BoulderCreationTests(BaseIntegrationTestClass):

    def test_get_gyms(self):
        """
        """
        # Given
        route = '/api/gym/list'
        # When
        resp = self.client.get(route)
        # Then
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json['gyms'][0]['name'], TEST_GYM_NAME)

    def test_get_walls(self):
        """
        """
        # Given
        route = f'/api/gym/{TEST_GYM_CODE}/walls'
        # When
        resp = self.client.get(route)
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
            fields.holds: [{'color': '#00ff00', 'x': 0, 'y': 0}]
        }
        # When
        resp = self.client.post(
            f'/api/boulders/{TEST_GYM_CODE}/{TEST_WALL_SECTION}/create', json=data)
        # Then
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json['created'], True)

    def test_create_boulder_failure_no_gym(self):
        """
        """
        # Given
        non_existing_gym = 'blabla'
        route = f'/api/boulders/{non_existing_gym}/{TEST_WALL_SECTION}/create'
        fields = BoulderFields()
        data = {
            fields.creator: 'test user',
            fields.difficulty: 'green',
            fields.feet: 'free',
            fields.name: 'test',
            fields.notes: "",
            fields.holds: [{'color': '#00ff00', 'x': 0, 'y': 0}]
        }
        # When
        resp = self.client.post(route, json=data)
        # Then
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json['created'], False)

    def test_create_boulder_failure_no_wall_section(self):
        """
        """
        # Given
        non_existing_wall_section = 'blabla'
        route = f'/api/boulders/{TEST_GYM_CODE}/{non_existing_wall_section}/create'
        fields = BoulderFields()
        data = {
            fields.creator: 'test user',
            fields.difficulty: 'green',
            fields.feet: 'free',
            fields.name: 'test',
            fields.notes: "",
            fields.holds: [{'color': '#00ff00', 'x': 0, 'y': 0}]
        }
        # When
        resp = self.client.post(route, json=data)
        # Then
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json['created'], False)

    def test_create_boulder_failure_no_data(self):
        """
        """
        # Given
        route = f'/api/boulders/{TEST_GYM_CODE}/{TEST_WALL_SECTION}/create'
        data = {}
        # When
        resp = self.client.post(route, json=data)
        # Then
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json['created'], False)

    def test_create_boulder_failure(self):
        """
        """
        # Given
        route = f'/api/boulders/{TEST_GYM_CODE}/{TEST_WALL_SECTION}/create'
        fields = BoulderFields()
        data = {
            fields.creator: 'test user',
            fields.difficulty: 'green',
            fields.feet: 'free',
            fields.name: 1,
            fields.notes: "",
            fields.holds: [{'color': '#00ff00', 'x': 0, 'y': 0}]
        }
        # When
        resp = self.client.post(route, json=data)
        # Then
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json['created'], False)
        self.assertListEqual(resp.json.get('errors').get(
            'name'), ['Not a valid string.'])


if __name__ == '__main__':
    unittest.main()
