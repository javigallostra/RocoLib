import datetime
from genericpath import isfile
import unittest
import random
from application import app

from api.schemas import CreateBoulderRequestValidator, BoulderFields
from marshmallow import ValidationError
from bson.objectid import ObjectId

from tests.tests_config import TEST_CREATOR, TEST_DIFFICULTY
from tests.tests_config import TEST_FEET, TEST_HOLDS, TEST_NAME
from tests.tests_config import  TEST_NOTES, TEST_WALL_SECTION

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
        'name': TEST_NAME,
        'rating': random.randint(1, 5),
        'raters': random.randint(1, 10),
        'wall_section': TEST_WALL_SECTION,
        'difficulty': TEST_DIFFICULTY,
        'feet': TEST_FEET,
        'holds': TEST_HOLDS,
        'notes': TEST_NOTES,
        'creator': TEST_CREATOR,
        'created_at': datetime.datetime.now(),
        'updated_at': datetime.datetime.now()
    }

class UtilsTests(unittest.TestCase):
    def test_get_credentials(self):
        # Given
        from utils.utils import get_creds_file
        with open('.env', 'r') as f:
            creds_file_before = f.read()
        # When
        creds = get_creds_file()
        # Then
        self.assertIsNotNone(creds)
        self.assertIs(type(creds), str)
        self.assertTrue(isfile(creds))
        with open('.env', 'r') as f:
            creds_file_after = f.read()
        self.assertEqual(creds_file_before, creds_file_after)

    def test_get_credentials_not_found(self):
        # Given
        from utils.utils import get_creds_file
        # When
        def not_a_file(): return ''.join(
            [chr(random.randint(97, 122)) for i in range(5)]) + '.txt'
        non_existing_file = not_a_file()
        while isfile(non_existing_file):
            non_existing_file = not_a_file()
        creds = get_creds_file(non_existing_file)
        # Then
        self.assertIsNotNone(creds)
        self.assertIs(type(creds), str)
        self.assertFalse(isfile(creds))
        self.assertEqual(creds, '')

    def test_make_boulder_data_valid_js(self):
        # Given
        from utils.utils import make_boulder_data_valid_js
        data = ['{\'a\': \'True\'}', '{\'a\': \'False\'}']
        expected_data = [{'a': 'true'}, {'a': 'false'}]
        # When
        processed_data = [make_boulder_data_valid_js(d) for d in data]
        # Then
        for d in processed_data:
            self.assertIsNotNone(d)
            self.assertIs(type(d), dict)
        self.assertListEqual(processed_data, expected_data)

    def test_make_boulder_data_valid_js_wrong_data_type(self):
        # Given
        from utils.utils import make_boulder_data_valid_js
        invalid_data = [{'a': 'b'}, ['aaa'], (1, 2), 4, 17.23]
        expected_data = [dict() for _ in range(len(invalid_data))]
        # When
        processed_data = [make_boulder_data_valid_js(d) for d in invalid_data]
        # Then
        for d in processed_data:
            self.assertIsNotNone(d)
            self.assertIs(type(d), dict)
        self.assertListEqual(processed_data, expected_data)

    def test_get_wall_image(self):
        # Given
        from utils.utils import get_wall_image
        gym = 'sancu'
        section = 's1'
        path = 'images/walls/'
        # When
        with app.app_context(), app.test_request_context():
            image = get_wall_image(gym=gym, section=section, walls_path=path)
        # Then
        self.assertIsNotNone(image)
        self.assertIs(type(image), str)
        self.assertEqual(image, f'/static/{path}{gym}/{section}.JPG')

    def test_get_time_since_creation(self):
        # Given
        from utils.utils import get_time_since_creation
        import datetime
        test_year = 2021
        test_time = f'{test_year}-01-01T00:00:00.0000'
        current = datetime.datetime.now()
        # When
        time_since = get_time_since_creation(test_time)
        # Then
        self.assertEqual(time_since, f'{current.year - test_year} {"years" if current.year - test_year > 1 else "year"}')

    def test_boulder_data_no_repetitions_postprocessing_decorator(self):
        # Given
        from db.mongodb_controller import postprocess_boulder_data

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
        self.assertIn('repetitions', single_boulder)
        self.assertEqual(single_boulder['repetitions'], 0)

        for b in boulder_list:
            self.assertIn('repetitions', b)
            self.assertEqual(b['repetitions'], 0)

        for b in boulder_dict['Items']:
            self.assertIn('repetitions', b)
            self.assertEqual(b['repetitions'], 0)

    def test_boulder_data_repetitions_postprocessing_decorator(self):
        # Given
        from db.mongodb_controller import postprocess_boulder_data
        repetitions = 23
        # When
        @postprocess_boulder_data
        def get_single_fake_boulder_data():
            b = get_fake_boulder_data()
            b['repetitions'] = repetitions
            return b

        @postprocess_boulder_data
        def get_fake_boulders_list():
            b_list = [
                get_fake_boulder_data(), 
                get_fake_boulder_data()
            ]
            for b in b_list:
                b['repetitions'] = repetitions
            return b_list

        @postprocess_boulder_data
        def get_fake_boulders_dict():
            b_list = [
                get_fake_boulder_data(), 
                get_fake_boulder_data()
            ]
            for b in b_list:
                b['repetitions'] = repetitions
            return dict(Items=b_list)

        single_boulder = get_single_fake_boulder_data()
        boulder_list = get_fake_boulders_list()
        boulder_dict = get_fake_boulders_dict()
        
        # Then
        self.assertIn('repetitions', single_boulder)
        self.assertEqual(single_boulder['repetitions'], repetitions)

        for b in boulder_list:
            self.assertIn('repetitions', b)
            self.assertEqual(b['repetitions'], repetitions)

        for b in boulder_dict['Items']:
            self.assertIn('repetitions', b)
            self.assertEqual(b['repetitions'], repetitions)

    def test_boulder_data_serialization(self):
        pass

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
            fields.holds: 'holds'
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


if __name__ == '__main__':
    unittest.main()
