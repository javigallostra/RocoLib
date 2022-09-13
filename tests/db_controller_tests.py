import unittest
from db.query_builder import QueryBuilder
from tests.tests_config import *

class QueryBuilderTests(unittest.TestCase):
    """
    Unittests for mongoDB query builder
    """
    def setUp(self):
        """
        Initialize query
        """
        self.query_builder = QueryBuilder()

    def test_query_repr(self):
        # Given
        self.query_builder.contained_in(TEST_FIELD, TEST_VALUES)
        # When
        repr_query = self.query_builder.__repr__()
        # Then
        self.assertEqual(
            repr_query, "{'$and': [{'test_field': {'$in': [1, 2, 3]}}]}")

    def test_query_str(self):
        # Given
        self.query_builder.contained_in(TEST_FIELD, TEST_VALUES)
        # When
        str_query = str(self.query_builder)
        # Then
        self.assertEqual(
            str_query, "{'$and': [{'test_field': {'$in': [1, 2, 3]}}]}")

    def test_reset_query(self):
        # Given
        test_query = self.query_builder.equal(TEST_FIELD, TEST_VALUE_STR)
        # When
        test_query.reset_query()
        # Then
        self.assertDictEqual(dict(), test_query.query)
        self.assertNotIn(ROOT_KEY, test_query.query.keys())

    def test_contained_in_query(self):
        # Given
        contained_in_query = self.query_builder.contained_in(
            TEST_FIELD, TEST_VALUES)
        # When
        raw_query = contained_in_query.query
        # Then
        self.assertEqual(dict, type(raw_query))
        self.assertIn(ROOT_KEY, raw_query.keys())
        self.assertEqual(list, type(raw_query[ROOT_KEY]))
        self.assertIn(TEST_FIELD, raw_query[ROOT_KEY][0].keys())
        self.assertIn(CONTAINED_IN_KEY,
                      raw_query[ROOT_KEY][0][TEST_FIELD].keys())
        self.assertEqual(type(TEST_VALUES), type(
            raw_query[ROOT_KEY][0][TEST_FIELD][CONTAINED_IN_KEY]))
        self.assertListEqual(
            TEST_VALUES, raw_query[ROOT_KEY][0][TEST_FIELD][CONTAINED_IN_KEY])

    def test_not_contained_in_query(self):
        # Given
        not_contained_in_query = self.query_builder.not_contained_in(
            TEST_FIELD, TEST_VALUES)
        # When
        raw_query = not_contained_in_query.query
        # Then
        self.assertEqual(dict, type(raw_query))
        self.assertIn(ROOT_KEY, raw_query.keys())
        self.assertEqual(list, type(raw_query[ROOT_KEY]))
        self.assertIn(TEST_FIELD, raw_query[ROOT_KEY][0].keys())
        self.assertIn(NOT_CONTAINED_IN_KEY,
                      raw_query[ROOT_KEY][0][TEST_FIELD].keys())
        self.assertEqual(type(TEST_VALUES), type(
            raw_query[ROOT_KEY][0][TEST_FIELD][NOT_CONTAINED_IN_KEY]))
        self.assertListEqual(
            TEST_VALUES, raw_query[ROOT_KEY][0][TEST_FIELD][NOT_CONTAINED_IN_KEY])

    def test_lower_in_query(self):
        # Given
        lower_in_query = self.query_builder.lower(TEST_FIELD, TEST_INT_VAL)
        # When
        raw_query = lower_in_query.query
        # Then
        self.assertEqual(dict, type(raw_query))
        self.assertIn(ROOT_KEY, raw_query.keys())
        self.assertEqual(list, type(raw_query[ROOT_KEY]))
        self.assertIn(TEST_FIELD, raw_query[ROOT_KEY][0].keys())
        self.assertIn(LOWER_KEY, raw_query[ROOT_KEY][0][TEST_FIELD].keys())
        self.assertEqual(type(TEST_INT_VAL), type(
            raw_query[ROOT_KEY][0][TEST_FIELD][LOWER_KEY]))
        self.assertEqual(
            TEST_INT_VAL, raw_query[ROOT_KEY][0][TEST_FIELD][LOWER_KEY])

    def test_lower_or_equal_in_query(self):
        # Given
        lower_or_equal_in_query = self.query_builder.lower_or_equal(
            TEST_FIELD, TEST_INT_VAL)
        # When
        raw_query = lower_or_equal_in_query.query
        # Then
        self.assertEqual(dict, type(raw_query))
        self.assertIn(ROOT_KEY, raw_query.keys())
        self.assertEqual(list, type(raw_query[ROOT_KEY]))
        self.assertIn(TEST_FIELD, raw_query[ROOT_KEY][0].keys())
        self.assertIn(LOWER_OR_EQUAL_KEY,
                      raw_query[ROOT_KEY][0][TEST_FIELD].keys())
        self.assertEqual(type(TEST_INT_VAL), type(
            raw_query[ROOT_KEY][0][TEST_FIELD][LOWER_OR_EQUAL_KEY]))
        self.assertEqual(
            TEST_INT_VAL, raw_query[ROOT_KEY][0][TEST_FIELD][LOWER_OR_EQUAL_KEY])

    def test_greater_in_query(self):
        # Given
        greater_in_query = self.query_builder.greater(TEST_FIELD, TEST_INT_VAL)
        # When
        raw_query = greater_in_query.query
        # Then
        self.assertEqual(dict, type(raw_query))
        self.assertIn(ROOT_KEY, raw_query.keys())
        self.assertEqual(list, type(raw_query[ROOT_KEY]))
        self.assertIn(TEST_FIELD, raw_query[ROOT_KEY][0].keys())
        self.assertIn(GREATER_KEY, raw_query[ROOT_KEY][0][TEST_FIELD].keys())
        self.assertEqual(type(TEST_INT_VAL), type(
            raw_query[ROOT_KEY][0][TEST_FIELD][GREATER_KEY]))
        self.assertEqual(
            TEST_INT_VAL, raw_query[ROOT_KEY][0][TEST_FIELD][GREATER_KEY])

    def test_greater_or_equal_in_query(self):
        # Given
        greater_or_equal_in_query = self.query_builder.greater_or_equal(
            TEST_FIELD, TEST_INT_VAL)
        # When
        raw_query = greater_or_equal_in_query.query
        # Then
        self.assertEqual(dict, type(raw_query))
        self.assertIn(ROOT_KEY, raw_query.keys())
        self.assertEqual(list, type(raw_query[ROOT_KEY]))
        self.assertIn(TEST_FIELD, raw_query[ROOT_KEY][0].keys())
        self.assertIn(GREATER_OR_EQUAL_KEY,
                      raw_query[ROOT_KEY][0][TEST_FIELD].keys())
        self.assertEqual(type(TEST_INT_VAL), type(
            raw_query[ROOT_KEY][0][TEST_FIELD][GREATER_OR_EQUAL_KEY]))
        self.assertEqual(
            TEST_INT_VAL, raw_query[ROOT_KEY][0][TEST_FIELD][GREATER_OR_EQUAL_KEY])

    def test_equal_in_query(self):
        # Given
        equal_in_query = self.query_builder.equal(TEST_FIELD, TEST_INT_VAL)
        # When
        raw_query = equal_in_query.query
        # Then
        self.assertEqual(dict, type(raw_query))
        self.assertIn(ROOT_KEY, raw_query.keys())
        self.assertEqual(list, type(raw_query[ROOT_KEY]))
        self.assertIn(TEST_FIELD, raw_query[ROOT_KEY][0].keys())
        self.assertIn(EQUAL_KEY, raw_query[ROOT_KEY][0][TEST_FIELD].keys())
        self.assertEqual(type(TEST_INT_VAL), type(
            raw_query[ROOT_KEY][0][TEST_FIELD][EQUAL_KEY]))
        self.assertEqual(
            TEST_INT_VAL, raw_query[ROOT_KEY][0][TEST_FIELD][EQUAL_KEY])

    def test_not_equal_in_query(self):
        # Given
        not_equal_in_query = self.query_builder.not_equal(
            TEST_FIELD, TEST_INT_VAL)
        # When
        raw_query = not_equal_in_query.query
        # Then
        self.assertEqual(dict, type(raw_query))
        self.assertIn(ROOT_KEY, raw_query.keys())
        self.assertEqual(list, type(raw_query[ROOT_KEY]))
        self.assertIn(TEST_FIELD, raw_query[ROOT_KEY][0].keys())
        self.assertIn(NOT_EQUAL_KEY, raw_query[ROOT_KEY][0][TEST_FIELD].keys())
        self.assertEqual(type(TEST_INT_VAL), type(
            raw_query[ROOT_KEY][0][TEST_FIELD][NOT_EQUAL_KEY]))
        self.assertEqual(
            TEST_INT_VAL, raw_query[ROOT_KEY][0][TEST_FIELD][NOT_EQUAL_KEY])

    def test_contains_text_in_query(self):
        # Given
        contains_text_in_query = self.query_builder.contains_text(
            TEST_FIELD, TEST_VALUE_STR)
        # When
        raw_query = contains_text_in_query.query
        # Then
        self.assertEqual(dict, type(raw_query))
        self.assertIn(ROOT_KEY, raw_query.keys())
        self.assertEqual(list, type(raw_query[ROOT_KEY]))
        self.assertIn(TEST_FIELD, raw_query[ROOT_KEY][0].keys())
        self.assertIn(CONTAINS_TEXT_KEY,
                      raw_query[ROOT_KEY][0][TEST_FIELD].keys())
        self.assertEqual(type(TEST_VALUE_STR), type(
            raw_query[ROOT_KEY][0][TEST_FIELD][CONTAINS_TEXT_KEY]))
        self.assertEqual(
            TEST_VALUE_STR, raw_query[ROOT_KEY][0][TEST_FIELD][CONTAINS_TEXT_KEY])

    def test_chain_queries(self):
        # Given
        chained_query = self.query_builder.contained_in(
            TEST_FIELD, TEST_VALUES).lower(TEST_FIELD, TEST_INT_VAL)
        # When
        raw_query = chained_query.query
        # Then
        self.assertEqual(dict, type(raw_query))
        self.assertIn(ROOT_KEY, raw_query.keys())
        self.assertEqual(list, type(raw_query[ROOT_KEY]))
        self.assertEqual(2, len(raw_query[ROOT_KEY]))


class DBControllerTests(unittest.TestCase):
    pass


if __name__ == '__main__':
    unittest.main()
