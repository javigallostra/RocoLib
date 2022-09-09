from datetime import datetime
import unittest
from application import app

from api.schemas import BoulderFields
from src.config import CREDS, CREDS_LOCAL
from tests.tests_config import TEST_GYM_NAME, TEST_GYM_CODE, TEST_COORDINATES
from tests.tests_config import TEST_WALL_NAME, TEST_WALL_SECTION, TEST_WALL_RADIUS
from tests.tests_config import TEST_CREATOR, TEST_DIFFICULTY_STRING, TEST_FEET, TEST_NAME, TEST_NOTES, TEST_HOLDS
from tests.tests_config import TEST_DIFFICULTY_INT, TEST_USERNAME, TEST_EMAIL, TEST_PASSWORD

from src.utils import set_creds_file
from tests.utils import add_user_with_ticklist, drop_users, get_db_connection
from tests.utils import create_walls_collection, add_wall, drop_boulders, add_boulder

API_VERSION = 'v1'


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
            CREDS_LOCAL)  # set development credentials for the application
        # connect to testing ddbb and get test client
        self.db = get_db_connection()
        self.client = app.test_client()
        # create test gym collection
        create_walls_collection(
            self.db,
            TEST_GYM_NAME,
            TEST_GYM_CODE,
            TEST_COORDINATES
        )
        # Add section to the test gym
        add_wall(
            db=self.db,
            gym_code=TEST_GYM_CODE,
            wall_name=TEST_WALL_NAME,
            wall_section=TEST_WALL_SECTION,
            wall_radius=TEST_WALL_RADIUS
        )
        # drop any boulder documents in the test gym
        drop_boulders(self.db, TEST_GYM_CODE)
        fields = BoulderFields()
        boulder_data = {
            fields.raters: 0,
            fields.rating: 0,
            fields.section: TEST_WALL_SECTION,
            fields.time: datetime.now().isoformat(),
            fields.creator: TEST_CREATOR,
            fields.difficulty: TEST_DIFFICULTY_INT,
            fields.feet: TEST_FEET,
            fields.name: TEST_NAME,
            fields.notes: TEST_NOTES,
            fields.holds: TEST_HOLDS
        }
        # Add a boulder to the test gym
        add_boulder(self.db, TEST_GYM_CODE, boulder_data)
        # drop all users
        drop_users(self.db)
        # add a test user
        add_user_with_ticklist(self.db, TEST_USERNAME,
                               TEST_PASSWORD, TEST_EMAIL)

    def tearDown(self):
        """
        Tear down method that will run after every test
        """
        set_creds_file(CREDS)
        self.db.client.close()


class APITests(BaseIntegrationTestClass):

    def test_get_gyms(self):
        """
        Get available gyms
        """
        # Given
        route = f'/api/{API_VERSION}/gym/list'
        # When
        resp = self.client.get(route)
        # Then
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json['gyms'][0]['name'], TEST_GYM_NAME)

    def test_get_walls(self):
        """
        Get available walls from a gym
        """
        # Given
        route = f'/api/{API_VERSION}/gym/{TEST_GYM_CODE}/walls'
        # When
        resp = self.client.get(route)
        # Then
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json['walls'][0]['image'], TEST_WALL_SECTION)

    def test_create_boulder_success(self):
        """
        Create a boulder for a given wall in a given gym
        """
        # Given
        fields = BoulderFields()
        data = {
            fields.creator: TEST_CREATOR,
            fields.difficulty: TEST_DIFFICULTY_STRING,
            fields.feet: TEST_FEET,
            fields.name: TEST_NAME,
            fields.notes: TEST_NOTES,
            fields.holds: TEST_HOLDS
        }
        # When
        resp = self.client.post(
            f'/api/{API_VERSION}/boulders/{TEST_GYM_CODE}/{TEST_WALL_SECTION}/create', json=data)
        # Then
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json['created'], True)

    def test_create_boulder_failure_no_gym(self):
        """
        Create a boulder in a non existing gym
        """
        # Given
        non_existing_gym = 'blabla'
        route = f'/api/{API_VERSION}/boulders/{non_existing_gym}/{TEST_WALL_SECTION}/create'
        fields = BoulderFields()
        data = {
            fields.creator: TEST_CREATOR,
            fields.difficulty: TEST_DIFFICULTY_STRING,
            fields.feet: TEST_FEET,
            fields.name: TEST_NAME,
            fields.notes: TEST_NOTES,
            fields.holds: TEST_HOLDS
        }
        # When
        resp = self.client.post(route, json=data)
        # Then
        self.assertEqual(resp.status_code, 404)

    def test_create_boulder_failure_no_wall_section(self):
        """
        Create a boulder in a non existing wall section
        """
        # Given
        non_existing_wall_section = 'blabla'
        route = f'/api/{API_VERSION}/boulders/{TEST_GYM_CODE}/{non_existing_wall_section}/create'
        fields = BoulderFields()
        data = {
            fields.creator: TEST_CREATOR,
            fields.difficulty: TEST_DIFFICULTY_STRING,
            fields.feet: TEST_FEET,
            fields.name: TEST_NAME,
            fields.notes: TEST_NOTES,
            fields.holds: TEST_HOLDS
        }
        # When
        resp = self.client.post(route, json=data)
        # Then
        self.assertEqual(resp.status_code, 404)

    def test_create_boulder_failure_no_data(self):
        """
        Create a boulder without data
        """
        # Given
        route = f'/api/{API_VERSION}/boulders/{TEST_GYM_CODE}/{TEST_WALL_SECTION}/create'
        data = {}
        errors = {
            'creator': ['Missing data for required field.'],
            'difficulty': ['Missing data for required field.'],
            'feet': ['Missing data for required field.'],
            'holds': ['Missing data for required field.'],
            'name': ['Missing data for required field.'],
            'notes': ['Missing data for required field.']
        }
        # When
        resp = self.client.post(route, json=data)
        # Then
        self.assertEqual(resp.status_code, 400)
        self.assertDictEqual(errors, resp.json['errors'])

    def test_create_boulder_failure(self):
        """
        Create a boulder with invalid data
        """
        # Given
        route = f'/api/{API_VERSION}/boulders/{TEST_GYM_CODE}/{TEST_WALL_SECTION}/create'
        fields = BoulderFields()
        data = {
            fields.creator: TEST_CREATOR,
            fields.difficulty: TEST_DIFFICULTY_STRING,
            fields.feet: TEST_FEET,
            fields.name: 123,
            fields.notes: TEST_NOTES,
            fields.holds: TEST_HOLDS
        }
        # When
        resp = self.client.post(route, json=data)
        # Then
        self.assertEqual(resp.status_code, 400)
        self.assertListEqual(resp.json.get('errors').get(
            'name'), ['Not a valid string.'])

    def test_create_user_no_username(self):
        """
        Create a user without a username.
        """
        # Given
        route = f'/api/{API_VERSION}/user/signup'
        data = {
            'email': TEST_EMAIL,
            'password': TEST_PASSWORD
        }
        # When
        resp = self.client.post(route, json=data)
        # Then
        self.assertEqual(resp.status_code, 400)
        self.assertListEqual(list(resp.json.get('errors').keys()), ['username'])

    def test_create_user_no_password(self):
        """
        Create a user without a password.
        """
        # Given
        route = f'/api/{API_VERSION}/user/signup'
        data = {
            'email': TEST_EMAIL,
            'username': TEST_USERNAME
        }
        # When
        resp = self.client.post(route, json=data)
        # Then
        self.assertEqual(resp.status_code, 400)
        self.assertListEqual(list(resp.json.get('errors').keys()), ['password'])

    def test_create_user_no_email(self):
        """
        Create a user without an email.
        """
        # Given
        route = f'/api/{API_VERSION}/user/signup'
        data = {
            'password': TEST_PASSWORD,
            'username': TEST_USERNAME
        }
        # When
        resp = self.client.post(route, json=data)
        # Then
        self.assertEqual(resp.status_code, 400)
        self.assertListEqual(list(resp.json.get('errors').keys()), ['email'])

    def test_create_user_no_data(self):
        """
        Create a user without an email.
        """
        # Given
        route = f'/api/{API_VERSION}/user/signup'
        data = {}
        # When
        resp = self.client.post(route, json=data)
        # Then
        self.assertEqual(resp.status_code, 400)
        self.assertListEqual(list(resp.json.get('errors').keys()), ['email', 'password', 'username'])

    def test_create_user_invalid_email(self):
        pass

    def test_create_user_repeated_username(self):
        """
        Create a user with an already taken username.
        """
        # Given
        route = f'/api/{API_VERSION}/user/signup'
        data = {
            'password': TEST_PASSWORD,
            'username': TEST_USERNAME,
            'email': 'fake_email@mail.com'
        }
        # When
        resp = self.client.post(route, json=data)
        # Then
        self.assertEqual(resp.status_code, 400)
        self.assertListEqual(list(resp.json.get('errors').keys()), ['username'])

    def test_create_user_repeated_email(self):
        """
        Create a user with an already taken email.
        """
        # Given
        route = f'/api/{API_VERSION}/user/signup'
        data = {
            'password': TEST_PASSWORD,
            'username': 'fake_username',
            'email': TEST_EMAIL
        }
        # When
        resp = self.client.post(route, json=data)
        # Then
        self.assertEqual(resp.status_code, 400)
        self.assertListEqual(list(resp.json.get('errors').keys()), ['email'])

    def test_create_user_valid(self):
        """
        Create a user with valid data.
        """
        # Given
        route = f'/api/{API_VERSION}/user/signup'
        data = {
            'password': 'fake_password',
            'username': 'fake_username',
            'email': 'fake_email@mail.com'
        }
        # When
        resp = self.client.post(route, json=data)
        # Then
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.json.get('username'), 'fake_username')

    def test_get_user_preferences(self):
        # TODO: implement test
        pass

    def test_set_user_preferences(self):
        # TODO: implement test
        pass

    def test_get_user_ticklist(self):
        """
        Get the test user's ticklist
        """
        # Given
        route = f'/api/{API_VERSION}/user/ticklist'
        user_data = {
            'username': TEST_USERNAME,
            'password': TEST_PASSWORD
        }
        resp = self.client.post(
            f'/api/{API_VERSION}/user/auth', json=user_data)
        token = resp.json.get('token')
        # When
        resp = self.client.get(
            route, headers={'Authorization': f'Bearer {token}'})
        # Then
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json.get('boulders')), 1)
        self.assertEqual(resp.json.get('boulders')[0].get('name'), TEST_NAME)

    def test_mark_boulder_as_done(self):
        """
        Mark a boulder as done.
        """
        # Given
        route = f'/api/{API_VERSION}/user/ticklist/boulder/done'
        user_data = {
            'username': TEST_USERNAME,
            'password': TEST_PASSWORD
        }
        # authenticate user and get token
        auth_resp = self.client.post(
            f'/api/{API_VERSION}/user/auth', json=user_data)
        token = auth_resp.json.get('token')

        fields = BoulderFields()
        data = {
            fields.creator: TEST_CREATOR,
            fields.difficulty: TEST_DIFFICULTY_STRING,
            fields.feet: TEST_FEET,
            fields.name: TEST_NAME,
            fields.notes: TEST_NOTES,
            fields.holds: TEST_HOLDS
        }
        resp = self.client.post(
            f'/api/{API_VERSION}/boulders/{TEST_GYM_CODE}/{TEST_WALL_SECTION}/create', json=data)

        boulder_id = resp.json.get('_id')

        # When
        resp = self.client.post(
            route,
            headers={'Authorization': f'Bearer {token}'},
            json={'boulder_id': boulder_id, 'gym': TEST_GYM_CODE}
        )
        # Then
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json.get('boulder_id'), boulder_id)
        self.assertTrue(resp.json.get('marked_as_done'))

    def test_mark_boulder_as_done_not_found(self):
        """
        Try to mark as a done a boulder that doesn't exist.
        """
        # Given
        route = f'/api/{API_VERSION}/user/ticklist/boulder/done'
        user_data = {
            'username': TEST_USERNAME,
            'password': TEST_PASSWORD
        }
        fake_boulder_id = 'abcd145236acd41763da12a1'
        # authenticate user and get token
        auth_resp = self.client.post(
            f'/api/{API_VERSION}/user/auth', json=user_data)
        token = auth_resp.json.get('token')
        # When
        resp = self.client.post(
            route,
            headers={'Authorization': f'Bearer {token}'},
            json={'boulder_id': fake_boulder_id, 'gym': TEST_GYM_CODE}
        )
        # Then
        self.assertEqual(resp.status_code, 404)
        self.assertFalse(resp.json.get('marked_as_done'))

    def test_mark_boulder_as_done_bad_request(self):
        """
        Try to mark a boulder as done via a bad request.
        """
        # Given
        route = f'/api/{API_VERSION}/user/ticklist/boulder/done'
        user_data = {
            'username': TEST_USERNAME,
            'password': TEST_PASSWORD
        }
        # authenticate user and get token
        auth_resp = self.client.post(
            f'/api/{API_VERSION}/user/auth', json=user_data)
        token = auth_resp.json.get('token')
        # When
        resp = self.client.post(
            route,
            headers={'Authorization': f'Bearer {token}'},
            json={'boulder_id': '', 'gym': ''}
        )
        # Then
        self.assertEqual(resp.status_code, 400)
        self.assertFalse(resp.json.get('marked_as_done'))
        self.assertDictEqual(resp.json.get('errors'), {
                             'boulder_id': 'Boulder id is required', 'gym': 'Gym is required'})


if __name__ == '__main__':
    unittest.main()
