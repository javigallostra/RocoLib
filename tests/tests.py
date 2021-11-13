from genericpath import isfile
import unittest
import random
from application import app

from  api.schemas import CreateBoulderRequestBody, CreateBoulderRequestValidator, BoulderFields
from marshmallow import ValidationError

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


class UtilsTests(unittest.TestCase):
    def test_get_credentials(self):
        # Given
        from utils.utils import get_creds_file
        from os.path import isfile
        with open('.env', 'r') as f:
            creds_file_before = f.read()
        # When
        creds = get_creds_file()
        with open('.env', 'r') as f:
            creds_file_after = f.read()
        # Then
        self.assertIsNotNone(creds)
        self.assertIs(type(creds), str)
        self.assertTrue(isfile(creds))
        self.assertEqual(creds_file_before, creds_file_after)

    def test_get_credentials_not_found(self):
        # Given
        from utils.utils import get_creds_file
        # When
        not_a_file = lambda : ''.join([chr(random.randint(97, 122)) for i in range(5)]) + '.txt'
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

    def test_make_boulder_data_valid_js_wrong_data(self):
        pass

    def test_make_boulder_data_valid_js_wrong_data_type(self):
        pass

    def test_get_wall_image(self):
        # Given
        from utils.utils import get_wall_image
        gym='sancu'
        section='s1'
        path='images/walls/'
        # When
        with app.app_context(), app.test_request_context():
            image = get_wall_image(gym=gym, section=section, walls_path=path)
        # Then
        self.assertIsNotNone(image)
        self.assertIs(type(image), str)
        self.assertEqual(image, f'/static/{path}{gym}/{section}.JPG')

    def test_get_wall_image_not_found(self):
        pass
    def test_get_wall_image_wrong_path(self):
        pass
    def test_get_wall_image_wrong_gym(self):
        pass
    def test_get_wall_image_wrong_section(self):
        pass
    def test_get_wall_image_wrong_path_and_section(self):
        pass
    def test_get_wall_image_wrong_path_and_gym(self):
        pass
    def test_get_wall_image_wrong_gym_and_section(self):
        pass
    def test_get_wall_image_wrong_path_and_gym_and_section(self):
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
