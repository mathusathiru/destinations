from utils import enter_query, generate_checkboxes, get_coordinates, get_destinations, hash_password, create_tables, save_search_history, get_search_history, get_most_popular_searches, search_history
from unittest.mock import patch, MagicMock
import unittest

import sqlite3
import requests
import bcrypt


class TestEnterQueryFunction(unittest.TestCase):
    def test_valid_query(self):
        query, error = enter_query("Hello")
        self.assertEqual(query, "Hello")
        self.assertIsNone(error)

    def test_short_query(self):
        query, error = enter_query("H")
        self.assertIsNone(query)
        self.assertEqual(error, "Error: query is too short (2+ characters needed)")

    def test_empty_query(self):
        query, error = enter_query("")
        self.assertIsNone(query)
        self.assertEqual(error, "Error: query is too short (2+ characters needed)")


class TestGenerateCheckboxes(unittest.TestCase):

    def test_generate_checkboxes(self):
        checkboxes_left, checkboxes_right = generate_checkboxes()

        expected_structure = (
            '<div class="form-check">\n'
            '    <input type="checkbox" class="form-check-input" name="categories" value="your_value" id="checkbox_your_id">\n'
            '    <label class="form-check-label" for="checkbox_your_id">Your Label</label>\n'
            '</div>'
        )

        self.assertIn(expected_structure, checkboxes_left)
        self.assertIn(expected_structure, checkboxes_right)


class TestGetCoordinatesFunction(unittest.TestCase):
    @patch("requests.get")
    def test_valid_location(self, mock_requests):
        response_data = {
            "status": {"code": 200},
            "total_results": 1,
            "results": [{"geometry": {"lat": 37.7749, "lng": -122.4194}}]
        }
        mock_requests.return_value.json.return_value = response_data

        latitude, longitude, error = get_coordinates("San Francisco, CA")
        self.assertEqual(latitude, 37.7749)
        self.assertEqual(longitude, -122.4194)
        self.assertIsNone(error)

    @patch("requests.get")
    def test_invalid_location(self, mock_requests):
        response_data = {
            "status": {"code": 200},
            "total_results": 0
        }
        mock_requests.return_value.json.return_value = response_data

        latitude, longitude, error = get_coordinates("Invalid Location")
        self.assertIsNone(latitude)
        self.assertIsNone(longitude)
        self.assertEqual(error, "Error: Location not found. Please use a valid location.")

    @patch("requests.get")
    def test_multiple_locations_or_invalid(self, mock_requests):
        response_data = {
            "status": {"code": 200},
            "total_results": 2
        }
        mock_requests.return_value.json.return_value = response_data

        latitude, longitude, error = get_coordinates("Some Place")
        self.assertIsNone(latitude)
        self.assertIsNone(longitude)
        self.assertEqual(error, "Error: Multiple locations or invalid location found. Check for misspellings or provide a more specific location.")

    @patch("requests.get")
    def test_error_status_code(self, mock_requests):
        response_data = {
            "status": {"code": 404, "message": "Not Found"}
        }
        mock_requests.return_value.json.return_value = response_data

        latitude, longitude, error = get_coordinates("Some Location")
        self.assertIsNone(latitude)
        self.assertIsNone(longitude)
        self.assertEqual(error, "Error 404: Not Found")


class TestGetDestinations(unittest.TestCase):
    @patch('requests.get')
    def test_get_destinations(self, mock_get):
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = b'{"results": [{"name": "Test Place", "location": {"formatted_address": "123 Main St"}}, {"location": {}}]}'
        mock_get.return_value = mock_response

        c = MagicMock()
        conn = MagicMock()
        result = get_destinations(40.712776, -74.005974, "food", c, conn, 1)

        self.assertEqual(result, [{"name": "Test Place", "location": {"formatted_address": "123 Main St"}}])
        
        c.execute.assert_called_with("INSERT INTO search_history (user_id, place_name, address) VALUES (?, ?, ?)", (1, "Test Place", "123 Main St"))
        conn.commit.assert_called()


class TestHashPassword(unittest.TestCase):
    def test_hash_password_valid(self):
        password = "MyStrongPassword123"
        hashed_password = hash_password(password)

        self.assertIsInstance(hashed_password, str)

        self.assertNotEqual(hashed_password, password)

        self.assertTrue(bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")))

    def test_hash_password_empty(self):
        password = ""
        hashed_password = hash_password(password)

        self.assertIsInstance(hashed_password, str)

        self.assertNotEqual(hashed_password, "")

    def test_hash_password_unicode(self):
        password = "😃MySecurePassword😃"
        hashed_password = hash_password(password)

        self.assertIsInstance(hashed_password, str)

        self.assertTrue(bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")))


class TestCreateTables(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()

    def tearDown(self):
        self.cursor.close()
        self.conn.close()

    def test_create_tables_users(self):
        create_tables(self.cursor)

        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        table_exists = self.cursor.fetchone()
        self.assertIsNotNone(table_exists)

        self.cursor.execute("PRAGMA table_info(users);")
        columns = self.cursor.fetchall()
        column_names = [col[1] for col in columns]
        self.assertIn("user_id", column_names)
        self.assertIn("username", column_names)
        self.assertIn("password", column_names)

    def test_create_tables_search_history(self):
        create_tables(self.cursor)

        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='search_history';")
        table_exists = self.cursor.fetchone()
        self.assertIsNotNone(table_exists)

        self.cursor.execute("PRAGMA table_info(search_history);")
        columns = self.cursor.fetchall()
        column_names = [col[1] for col in columns]
        self.assertIn("search_id", column_names)
        self.assertIn("user_id", column_names)
        self.assertIn("place_name", column_names)
        self.assertIn("address", column_names)
        self.assertIn("timestamp", column_names)

        self.cursor.execute("PRAGMA foreign_key_list(search_history);")
        foreign_keys = self.cursor.fetchall()
        self.assertEqual(len(foreign_keys), 1)
        self.assertEqual(foreign_keys[0][2], "users")
        self.assertEqual(foreign_keys[0][3], "user_id")


class TestSaveSearchHistory(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()
        create_tables(self.cursor)

    def tearDown(self):
        self.cursor.close()
        self.conn.close()

    def test_save_search_history_valid(self):
        user_id = 1
        results = [
            {"name": "Place A", "location": {"formatted_address": "Address A"}},
            {"name": "Place B", "location": {"formatted_address": "Address B"}},
            {"name": "Place C", "location": {"formatted_address": "Address C"}},
        ]

        save_search_history(self.cursor, self.conn, user_id, results)

        self.cursor.execute("SELECT user_id, place_name, address FROM search_history;")
        saved_data = self.cursor.fetchall()

        self.assertEqual(len(saved_data), len(results))

        for i, result in enumerate(results):
            self.assertEqual(saved_data[i][0], user_id)
            self.assertEqual(saved_data[i][1], result["name"])
            self.assertEqual(saved_data[i][2], result["location"]["formatted_address"])


class TestGetSearchHistory(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.c = self.conn.cursor()
        create_tables(self.c)

    def tearDown(self):
        self.conn.close()

    def test_get_search_history(self):
        user_id = 1
        test_data = [
            ('Place A', 'Address A', '2023-08-01 10:00:00'),
            ('Place B', 'Address B', '2023-08-02 15:30:00'),
            ('Place C', 'Address C', '2023-08-03 09:45:00'),
        ]
        for data in test_data:
            self.c.execute("INSERT INTO search_history (user_id, place_name, address, timestamp) "
                           "VALUES (?, ?, ?, ?)", (user_id, data[0], data[1], data[2]))
        self.conn.commit()

        result = get_search_history(self.c, user_id)

        expected_result = sorted(test_data, key=lambda x: x[2], reverse=True)
        actual_result = sorted(result, key=lambda x: x[2], reverse=True)

        self.assertEqual(actual_result, expected_result)


class TestGetMostPopularSearches(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.c = self.conn.cursor()
        create_tables(self.c)

    def tearDown(self):
        self.conn.close()

    def test_get_most_popular_searches(self):
        user_id = 1
        test_data = [
            ('Place A', 'Address A'),
            ('Place A', 'Address A'),
            ('Place B', 'Address B'),
            ('Place B', 'Address B'),
            ('Place B', 'Address B'),
            ('Place C', 'Address C'),
            ('Place C', 'Address C'),
            ('Place C', 'Address C'),
            ('Place D', 'Address D'),
            ('Place D', 'Address D'),
        ]
        for data in test_data:
            self.c.execute("INSERT INTO search_history (user_id, place_name, address) "
                           "VALUES (?, ?, ?)", (user_id, data[0], data[1]))
        self.conn.commit()
        result = get_most_popular_searches(self.c, user_id)

        expected_result = sorted(result, key=lambda x: (-x[2], x[0], x[1]))
        actual_result = sorted(result, key=lambda x: (-x[2], x[0], x[1]))

        self.assertEqual(actual_result, expected_result)


class TestSearchKeyword(unittest.TestCase):

    def setUp(self):
        self.conn = sqlite3.connect(':memory:')
        self.c = self.conn.cursor()
        create_tables(self.c)

    def tearDown(self):
        self.conn.close()

    def test_search_history(self):
        user_id = 1
        test_data = [
            ('Place A', 'Address A', '2023-08-01 10:00:00'),
            ('Place B', 'Keyword B', '2023-08-02 15:30:00'),
            ('Keyword C', 'Address C', '2023-08-03 09:45:00'),
            ('Keyword D', 'Keyword D', '2023-08-04 12:00:00'),
            ('Place E', 'Address E', '2023-08-05 14:30:00'),
        ]
        for data in test_data:
            self.c.execute("INSERT INTO search_history (user_id, place_name, address, timestamp) "
                           "VALUES (?, ?, ?, ?)", (user_id, data[0], data[1], data[2]))
        self.conn.commit()

        keyword = 'Keyword'
        result = search_history(self.c, user_id, keyword)

        expected_result = [
            ('Place B', 'Keyword B', '2023-08-02 15:30:00'),
            ('Keyword C', 'Address C', '2023-08-03 09:45:00'),
            ('Keyword D', 'Keyword D', '2023-08-04 12:00:00'),
        ]
        self.assertEqual(result, expected_result)


if __name__ == '__main__':
    unittest.main()
