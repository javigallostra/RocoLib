import unittest

from db.query_builder import QueryBuilder

TEST_FIELD = 'test_field'
TEST_VALUES = [1, 2, 3]
TEST_VALUE = 'test_val'
ROOT_KEY = '$and'
CONTAINED_IN_KEY = '$in'

class QueryBuilderTests(unittest.TestCase):
    def setUp(self):
        self.query_builder = QueryBuilder()

    def test_contained_in_query(self):
        # Given
        contained_in_query = self.query_builder.contained_in(TEST_FIELD, TEST_VALUES)
        # When
        raw_query = contained_in_query.query
        # Then
        self.assertEqual(dict, type(raw_query))
        self.assertIn(ROOT_KEY, raw_query.keys())
        self.assertEqual(list, type(raw_query[ROOT_KEY]))
        self.assertIn(TEST_FIELD, raw_query[ROOT_KEY][0].keys())
        self.assertIn(CONTAINED_IN_KEY, raw_query[ROOT_KEY][0][TEST_FIELD].keys())
        self.assertEqual(list, type(raw_query[ROOT_KEY][0][TEST_FIELD][CONTAINED_IN_KEY]))
        self.assertListEqual(TEST_VALUES, raw_query[ROOT_KEY][0][TEST_FIELD][CONTAINED_IN_KEY])

    def test_reset_query(self):
        # Given
        test_query = self.query_builder.equal(TEST_FIELD, TEST_VALUE)
        # When
        test_query.reset_query()
        # Then
        self.assertDictEqual(dict(), test_query.query)
        self.assertNotIn(ROOT_KEY, test_query.query.keys())
        

class DBControllerTests(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
