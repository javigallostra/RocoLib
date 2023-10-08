import datetime
import unittest
import random
from genericpath import isfile

from application import app
from marshmallow import ValidationError
from bson.objectid import ObjectId

from api.schemas import CreateBoulderRequestValidator, BoulderFields
from src.config import ITEMS
from src.models import User, UserPreferences

from tests.tests_config import TEST_CREATOR, TEST_DIFFICULTY_INT, TEST_GYM_CODE, TEST_ID
from tests.tests_config import TEST_FEET, TEST_HOLDS, TEST_NAME
from tests.tests_config import TEST_NOTES, TEST_WALL_SECTION
from tests.utils import FakeRequest

# class BaseAPITestClass(unittest.TestCase):
#     """
#     BaseClass for testing
#     """

#     def setUp(self):
#         """
#         Set up method that will run before every test
#         """
#         pass

#     def tearDown(self):
#         """
#         Tear down method that will run after every test
#         """
#         pass


def get_fake_boulder_data():
    return {
        '_id': ObjectId(TEST_ID),
        'name': TEST_NAME,
        'rating': random.randint(1, 5),
        'raters': random.randint(1, 10),
        'wall_section': TEST_WALL_SECTION,
        'difficulty': TEST_DIFFICULTY_INT,
        'feet': TEST_FEET,
        'holds': TEST_HOLDS,
        'notes': TEST_NOTES,
        'creator': TEST_CREATOR,
        'created_at': datetime.datetime.now(),
        'updated_at': datetime.datetime.now()
    }


class UtilsTests(unittest.TestCase):
    """
    Test utility functions
    """
    def test_get_credentials(self):
        # Given
        from os.path import exists
        from src.utils import get_creds_file
        with open('.ddbb.env', 'r') as f:
            creds_file_before = f.read()
        # When
        if exists(creds_file_before):
            creds = get_creds_file()
            # Then
            self.assertIsNotNone(creds)
            self.assertTrue(isinstance(creds, str))
            self.assertTrue(isfile(creds))
            with open('.ddbb.env', 'r') as f:
                creds_file_after = f.read()
            self.assertEqual(creds_file_before, creds_file_after)

    def test_get_credentials_not_found(self):
        # Given
        from src.utils import get_creds_file
        # When
        def not_a_file(): return ''.join(
            [chr(random.randint(97, 122)) for i in range(5)]) + '.txt'
        non_existing_file = not_a_file()
        creds = get_creds_file(non_existing_file)
        # Then
        self.assertIsNotNone(creds)
        self.assertTrue(isinstance(creds, str))
        self.assertFalse(isfile(creds))
        self.assertEqual(creds, '')

    def test_make_boulder_data_valid_js(self):
        # Given
        from src.utils import make_boulder_data_valid_js
        data = ['{\'a\': \'True\'}', '{\'a\': \'False\'}']
        expected_data = [{'a': 'true'}, {'a': 'false'}]
        # When
        processed_data = [make_boulder_data_valid_js(d) for d in data]
        # Then
        for d in processed_data:
            self.assertIsNotNone(d)
            self.assertTrue(isinstance(d, dict))
        self.assertListEqual(processed_data, expected_data)

    def test_make_boulder_data_valid_js_wrong_data_type(self):
        # Given
        from src.utils import make_boulder_data_valid_js
        invalid_data = [{'a': 'b'}, ['aaa'], (1, 2), 4, 17.23]
        expected_data = [dict() for _ in range(len(invalid_data))]
        # When
        processed_data = [make_boulder_data_valid_js(d) for d in invalid_data]
        # Then
        for d in processed_data:
            self.assertIsNotNone(d)
            self.assertTrue(isinstance(d, dict))
        self.assertListEqual(processed_data, expected_data)

    def test_get_wall_image(self):
        # Given
        from src.utils import get_wall_image
        gym = 'sancu'
        section = 's1'
        path = 'images/walls/'
        # When
        with app.app_context(), app.test_request_context():
            image = get_wall_image(gym=gym, section=section, walls_path=path)
        # Then
        self.assertIsNotNone(image)
        self.assertTrue(isinstance(image, str))
        self.assertEqual(image, f'/static/{path}{gym}/{section}.JPG')

    def test_get_time_since_creation(self):
        # Given
        from src.utils import get_time_since_creation
        import datetime
        test_year = 2021
        test_time = f'{test_year}-01-01T00:00:00.0000'
        current = datetime.datetime.now()
        # When
        time_since = get_time_since_creation(test_time)
        # Then
        self.assertEqual(
            time_since, f'{current.year - test_year} {"years" if current.year - test_year > 1 else "year"}')

    def test_boulder_data_no_repetitions_postprocessing_decorator(self):
        # Given
        from db.mongodb_controller import postprocess_boulder_data
        rep_key = 'repetitions'
        # When

        @postprocess_boulder_data
        def get_single_fake_boulder_data():
            return get_fake_boulder_data()

        @postprocess_boulder_data
        def get_fake_boulders_list():
            return [
                get_fake_boulder_data(),
                get_fake_boulder_data()
            ]

        @postprocess_boulder_data
        def get_fake_boulders_dict():
            return dict(
                Items=[
                    get_fake_boulder_data(),
                    get_fake_boulder_data()
                ]
            )

        single_boulder = get_single_fake_boulder_data()
        boulder_list = get_fake_boulders_list()
        boulder_dict = get_fake_boulders_dict()

        # Then
        self.assertIn(rep_key, single_boulder)
        self.assertEqual(single_boulder[rep_key], 0)

        for b in boulder_list:
            self.assertIn(rep_key, b)
            self.assertEqual(b[rep_key], 0)

        for b in boulder_dict[ITEMS]:
            self.assertIn(rep_key, b)
            self.assertEqual(b[rep_key], 0)

    def test_boulder_data_repetitions_postprocessing_decorator(self):
        # Given
        from db.mongodb_controller import postprocess_boulder_data
        repetitions = 23
        rep_key = 'repetitions'

        # When
        @postprocess_boulder_data
        def get_single_fake_boulder_data():
            b = get_fake_boulder_data()
            b[rep_key] = repetitions
            return b

        @postprocess_boulder_data
        def get_fake_boulders_list():
            b_list = [
                get_fake_boulder_data(),
                get_fake_boulder_data()
            ]
            for b in b_list:
                b[rep_key] = repetitions
            return b_list

        @postprocess_boulder_data
        def get_fake_boulders_dict():
            b_list = [
                get_fake_boulder_data(),
                get_fake_boulder_data()
            ]
            for b in b_list:
                b[rep_key] = repetitions
            return dict(Items=b_list)

        single_boulder = get_single_fake_boulder_data()
        boulder_list = get_fake_boulders_list()
        boulder_dict = get_fake_boulders_dict()

        # Then
        self.assertIn(rep_key, single_boulder)
        self.assertEqual(single_boulder[rep_key], repetitions)

        for b in boulder_list:
            self.assertIn(rep_key, b)
            self.assertEqual(b[rep_key], repetitions)

        for b in boulder_dict[ITEMS]:
            self.assertIn(rep_key, b)
            self.assertEqual(b[rep_key], repetitions)

    def test_boulder_data_serialization(self):
        # Given
        from db.mongodb_controller import serializable
        id_key = '_id'

        # When
        @serializable
        def get_boulder_data():
            return get_fake_boulder_data()

        @serializable
        def get_boulder_data_list():
            return [
                get_fake_boulder_data(),
                get_fake_boulder_data()
            ]

        @serializable
        def get_boulder_data_dict():
            return dict(
                Items=[
                    get_fake_boulder_data(),
                    get_fake_boulder_data()
                ]
            )

        @serializable
        def get_boulder_data_dict_single_item():
            return dict(Items=get_fake_boulder_data())

        boulder = get_boulder_data()
        boulder_list = get_boulder_data_list()
        boulder_dict = get_boulder_data_dict()
        boulder_dict_single = get_boulder_data_dict_single_item()

        # Then
        self.assertEqual(TEST_ID, boulder[id_key])
        self.assertTrue(isinstance(boulder[id_key], str))
        for b in boulder_list:
            self.assertEqual(TEST_ID, b[id_key])
            self.assertTrue(isinstance(b[id_key], str))
        for b in boulder_dict[ITEMS]:
            self.assertEqual(TEST_ID, b[id_key])
            self.assertTrue(isinstance(b[id_key], str))
        self.assertEqual(TEST_ID, boulder_dict_single[ITEMS][id_key])
        self.assertTrue(
            isinstance(boulder_dict_single[ITEMS][id_key], str)
        )


class BoulderCreationTests(unittest.TestCase):

    def test_create_boulder(self):
        """
        """
        # Given
        fields = BoulderFields()
        data = {
            fields.raters: 'a',
            fields.rating: 'a',
            fields.section: 1,
            fields.creator: 2,
            fields.difficulty: [],
            fields.feet: dict(),
            fields.name: 5,
            fields.time: 23,
            fields.notes: None,
            fields.holds: 'holds',
            fields.is_project: 'a'
        }
        # When
        with self.assertRaises(ValidationError) as context:
            _ = CreateBoulderRequestValidator().load(data)
        # Then
        self.assertIn('raters', context.exception.messages)
        self.assertIn('rating', context.exception.messages)
        self.assertIn('section', context.exception.messages)
        self.assertIn('creator', context.exception.messages)
        self.assertIn('difficulty', context.exception.messages)
        self.assertIn('feet', context.exception.messages)
        self.assertIn('name', context.exception.messages)
        self.assertIn('time', context.exception.messages)
        self.assertIn('notes', context.exception.messages)
        self.assertIn('holds', context.exception.messages)
        self.assertIn('is_project', context.exception.messages)


class UserModelTests(unittest.TestCase):
    def test_user_creation(self):
        # Given
        user_id = '1234'
        # When
        user = User(id=user_id)
        # Then
        self.assertNotEqual(user.preferences, None)
        self.assertEqual(user.preferences.user_id, user_id)
        self.assertEqual(user.preferences.hold_detection_disabled, False)
        self.assertEqual(user.preferences.show_latest_walls_only, True)

    def test_update_user_prefs(self):
        # Given
        from src.utils import update_user_prefs
        user_id = '1234'
        # When
        current_user = User(id=user_id)
        request = FakeRequest(
            form=dict(gym=TEST_GYM_CODE, latestWallSwitch=False, holdDetectionSwitch=True))
        modified, updated_user = update_user_prefs(request, current_user)
        # Then
        self.assertEqual(modified, True)
        self.assertEqual(updated_user.preferences.default_gym, TEST_GYM_CODE)
        self.assertEqual(
            updated_user.preferences.hold_detection_disabled, True)
        self.assertEqual(
            updated_user.preferences.show_latest_walls_only, False)

    def test_no_update_user_prefs(self):
        # Given
        from src.utils import update_user_prefs
        user_id = '1234'
        preferences = UserPreferences(
            user_id=user_id, default_gym=TEST_GYM_CODE)
        user_data = {'id': user_id, 'user_preferences': preferences}
        # When
        current_user = User(user_data)
        request = FakeRequest(
            form=dict(gym=TEST_GYM_CODE, latestWallSwitch=True, holdDetectionSwitch=False))
        modified, updated_user = update_user_prefs(request, current_user)
        # Then
        self.assertEqual(modified, False)
        self.assertEqual(updated_user.preferences.default_gym, TEST_GYM_CODE)
        self.assertEqual(
            updated_user.preferences.hold_detection_disabled, False)
        self.assertEqual(updated_user.preferences.show_latest_walls_only, True)

    def test_get_hold_detection_active(self):
        # Given
        from src.utils import get_hold_detection_active
        user_id = '1234'
        # When
        current_user = User(id=user_id)
        active = get_hold_detection_active(current_user)
        # Then
        self.assertEqual(active, True)

    def test_get_show_only_latest_wall_sets(self):
        # Given
        from src.utils import get_show_only_latest_wall_sets
        user_id = '1234'
        # When
        current_user = User(id=user_id)
        only_latest = get_show_only_latest_wall_sets(current_user)
        # Then
        self.assertEqual(only_latest, True)


if __name__ == '__main__':
    unittest.main()
