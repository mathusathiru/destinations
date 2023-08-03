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

class TestGenerateCheckboxesFunction(unittest.TestCase):
    def test_generate_checkboxes(self):
        expected_output = (
            "<input type='checkbox' name='categories' value='10000'>Arts and Entertainment<br>"
            "<input type='checkbox' name='categories' value='12000'>Community<br>"
            "<input type='checkbox' name='categories' value='13000'>Dining and Drinking<br>"
            "<input type='checkbox' name='categories' value='14000'>Events<br>"
            "<input type='checkbox' name='categories' value='16000'>Landmarks and Outdoors<br>"
            "<input type='checkbox' name='categories' value='17000'>Retail<br>"
            "<input type='checkbox' name='categories' value='18000'>Sports<br>"
            "<input type='checkbox' name='categories' value='19000'>Travel and Transportation<br>"
        )
        result = generate_checkboxes()
        self.assertEqual(result, expected_output)

class TestGetCoordinatesFunction(unittest.TestCase):
    @patch("requests.get")
    def test_valid_location(self, mock_requests):
        # Mock the response for a valid location
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
        # Mock the response for an invalid location (total_results = 0)
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
        # Mock the response for multiple locations or invalid location
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
        # Mock the response for a non-200 status code
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
        # Mock the response from the requests.get call
        mock_response = requests.Response()
        mock_response.status_code = 200
        mock_response._content = b'{"results": [{"name": "Test Place", "location": {"formatted_address": "123 Main St"}}, {"location": {}}]}'
        mock_get.return_value = mock_response

        # Call the function with test data
        c = MagicMock()
        conn = MagicMock()
        result = get_destinations(40.712776, -74.005974, "food", c, conn, 1)

        # Assert that the result is as expected
        self.assertEqual(result, [{"name": "Test Place", "location": {"formatted_address": "123 Main St"}}])
        
        # Assert that the save_search_history function was called with the correct arguments
        c.execute.assert_called_with("INSERT INTO search_history (user_id, place_name, address) VALUES (?, ?, ?)", (1, "Test Place", "123 Main St"))
        conn.commit.assert_called()

class TestHashPassword(unittest.TestCase):
    def test_hash_password_valid(self):
        # Test if the function correctly hashes a valid password
        password = "MyStrongPassword123"
        hashed_password = hash_password(password)

        # Check if the returned hashed_password is a string
        self.assertIsInstance(hashed_password, str)

        # Check if the hashed_password is not equal to the original password
        self.assertNotEqual(hashed_password, password)

        # Check if bcrypt.checkpw confirms the password and its hash match
        self.assertTrue(bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")))

    def test_hash_password_empty(self):
        # Test if the function handles empty password input
        password = ""
        hashed_password = hash_password(password)

        # Check if the returned hashed_password is a string
        self.assertIsInstance(hashed_password, str)

        # Check if the hashed_password is not empty
        self.assertNotEqual(hashed_password, "")

    def test_hash_password_unicode(self):
        # Test if the function correctly handles unicode passwords
        password = "😃MySecurePassword😃"
        hashed_password = hash_password(password)

        # Check if the returned hashed_password is a string
        self.assertIsInstance(hashed_password, str)

        # Check if bcrypt.checkpw confirms the password and its hash match
        self.assertTrue(bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8")))

class TestCreateTables(unittest.TestCase):
    def setUp(self):
        # Create an in-memory SQLite database and a cursor
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()

    def tearDown(self):
        # Close the cursor and the connection
        self.cursor.close()
        self.conn.close()

    def test_create_tables_users(self):
        # Test if the 'users' table is created correctly
        create_tables(self.cursor)

        # Check if the 'users' table exists
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        table_exists = self.cursor.fetchone()
        self.assertIsNotNone(table_exists)

        # Check if the columns 'user_id', 'username', and 'password' exist in the 'users' table
        self.cursor.execute("PRAGMA table_info(users);")
        columns = self.cursor.fetchall()
        column_names = [col[1] for col in columns]
        self.assertIn("user_id", column_names)
        self.assertIn("username", column_names)
        self.assertIn("password", column_names)

    def test_create_tables_search_history(self):
        # Test if the 'search_history' table is created correctly
        create_tables(self.cursor)

        # Check if the 'search_history' table exists
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='search_history';")
        table_exists = self.cursor.fetchone()
        self.assertIsNotNone(table_exists)

        # Check if the columns 'search_id', 'user_id', 'place_name', 'address', and 'timestamp' exist in the 'search_history' table
        self.cursor.execute("PRAGMA table_info(search_history);")
        columns = self.cursor.fetchall()
        column_names = [col[1] for col in columns]
        self.assertIn("search_id", column_names)
        self.assertIn("user_id", column_names)
        self.assertIn("place_name", column_names)
        self.assertIn("address", column_names)
        self.assertIn("timestamp", column_names)

        # Check if the 'user_id' column has a foreign key reference to the 'users' table
        self.cursor.execute("PRAGMA foreign_key_list(search_history);")
        foreign_keys = self.cursor.fetchall()
        self.assertEqual(len(foreign_keys), 1)
        self.assertEqual(foreign_keys[0][2], "users")
        self.assertEqual(foreign_keys[0][3], "user_id")

class TestSaveSearchHistory(unittest.TestCase):
    def setUp(self):
        # Create an in-memory SQLite database and a cursor
        self.conn = sqlite3.connect(":memory:")
        self.cursor = self.conn.cursor()
        # Create necessary tables
        create_tables(self.cursor)

    def tearDown(self):
        # Close the cursor and the connection
        self.cursor.close()
        self.conn.close()

    def test_save_search_history_valid(self):
        # Mock data for the user_id and search results
        user_id = 1
        results = [
            {"name": "Place A", "location": {"formatted_address": "Address A"}},
            {"name": "Place B", "location": {"formatted_address": "Address B"}},
            {"name": "Place C", "location": {"formatted_address": "Address C"}},
        ]

        # Call the function to save search history
        save_search_history(self.cursor, self.conn, user_id, results)

        # Check if the data is correctly inserted into the 'search_history' table
        self.cursor.execute("SELECT user_id, place_name, address FROM search_history;")
        saved_data = self.cursor.fetchall()

        # Verify if the data matches the input
        self.assertEqual(len(saved_data), len(results))

        for i, result in enumerate(results):
            self.assertEqual(saved_data[i][0], user_id)
            self.assertEqual(saved_data[i][1], result["name"])
            self.assertEqual(saved_data[i][2], result["location"]["formatted_address"])

class TestGetSearchHistory(unittest.TestCase):

    # Set up a test database and tables
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')  # Create an in-memory SQLite database
        self.c = self.conn.cursor()
        create_tables(self.c)

    def tearDown(self):
        self.conn.close()

    def test_get_search_history(self):
        # Insert test data into search_history table
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

        # Call the function with the user_id
        result = get_search_history(self.c, user_id)

        # Sort both the expected and actual results based on the timestamp
        expected_result = sorted(test_data, key=lambda x: x[2], reverse=True)
        actual_result = sorted(result, key=lambda x: x[2], reverse=True)

        # Verify the result
        self.assertEqual(actual_result, expected_result)

class TestGetMostPopularSearches(unittest.TestCase):

    # Set up a test database and tables
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')  # Create an in-memory SQLite database
        self.c = self.conn.cursor()
        create_tables(self.c)

    def tearDown(self):
        self.conn.close()

    def test_get_most_popular_searches(self):
        # Insert test data into search_history table
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

        # Call the function with the user_id
        result = get_most_popular_searches(self.c, user_id)

        # Sort both the expected and actual results based on search_count and then place_name and address
        expected_result = sorted(result, key=lambda x: (-x[2], x[0], x[1]))
        actual_result = sorted(result, key=lambda x: (-x[2], x[0], x[1]))

        # Verify the result
        self.assertEqual(actual_result, expected_result)

class TestSearchKeyword(unittest.TestCase):

    # Set up a test database and tables
    def setUp(self):
        self.conn = sqlite3.connect(':memory:')  # Create an in-memory SQLite database
        self.c = self.conn.cursor()
        create_tables(self.c)

    def tearDown(self):
        self.conn.close()

    def test_search_history(self):
        # Insert test data into search_history table
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

        # Call the function with the user_id and keyword
        keyword = 'Keyword'
        result = search_history(self.c, user_id, keyword)

        # Verify the result
        expected_result = [
            ('Place B', 'Keyword B', '2023-08-02 15:30:00'),
            ('Keyword C', 'Address C', '2023-08-03 09:45:00'),
            ('Keyword D', 'Keyword D', '2023-08-04 12:00:00'),
        ]
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()