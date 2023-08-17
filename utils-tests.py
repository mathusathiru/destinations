from utils import enter_query, generate_checkboxes, generate_radio_buttons, get_coordinates, get_destinations, requests
from unittest.mock import Mock
import unittest


class TestUtils(unittest.TestCase):
    def test_enter_query(self):
        query, error = enter_query("test")
        self.assertEqual(query, "test")
        self.assertIsNone(error)

        query, error = enter_query("t")
        self.assertIsNone(query)
        self.assertEqual(error, "Error: query is too short (2+ characters needed)")

    def test_generate_checkboxes(self):
        checkboxes = generate_checkboxes()
        self.assertIn('Arts and Entertainment', checkboxes)
        self.assertIn('Community', checkboxes)
        self.assertIn('Dining and Drinking', checkboxes)
        self.assertIn('Events', checkboxes)
        self.assertIn('Landmarks and Outdoors', checkboxes)
        self.assertIn('Retail', checkboxes)
        self.assertIn('Sports', checkboxes)
        self.assertIn('Travel and Transportation', checkboxes)

    def test_generate_radio_buttons(self):
        radius_buttons = generate_radio_buttons()
        self.assertIn('500', radius_buttons)
        self.assertIn('1000', radius_buttons)
        self.assertIn('2500', radius_buttons)
        self.assertIn('5000', radius_buttons)
        self.assertIn('10000', radius_buttons)

    def test_get_coordinates(self):
        mock_response = Mock()
        mock_response.json.return_value = {
            "status": {"code": 200},
            "total_results": 1,
            "results": [{"geometry": {"lat": 1.0, "lng": 2.0}}]
        }

        requests.get = Mock(return_value=mock_response)

        lat, lng, error = get_coordinates("test")
        self.assertEqual(lat, 1.0)
        self.assertEqual(lng, 2.0)
        self.assertIsNone(error)

    def test_get_destinations(self):
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {
                    "location": {
                        "formatted_address": "test address"
                    }
                }
            ]
        }
        mock_response.status_code = 200

        requests.get = Mock(return_value=mock_response)

        destinations = get_destinations(1.0, 2.0, "", 1000, None, None)
        self.assertEqual(len(destinations), 1)


if __name__ == '__main__':
    unittest.main()
