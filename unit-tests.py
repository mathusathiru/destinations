from database import db, User, SearchHistory, hash_password, save_history, get_history, get_top_searches, search_history
from utils import enter_query, generate_checkboxes, generate_radio_buttons, get_coordinates, get_destinations, requests
from unittest.mock import Mock
from app import app
import unittest


class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_home(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)

    def test_search_page(self):
        response = self.app.get("/search.html")
        self.assertEqual(response.status_code, 200)

    def test_register(self):
        response = self.app.get("/register.html")
        self.assertEqual(response.status_code, 200)

    def test_login_handler(self):
        response = self.app.get("/login.html")
        self.assertEqual(response.status_code, 200)

    def test_account(self):
        response = self.app.get("/account.html")
        self.assertEqual(response.status_code, 302)

    def test_logout(self):
        response = self.app.get("/logout")
        self.assertEqual(response.status_code, 302)

    def test_search_location(self):
        response = self.app.post("/search", data={"search": "Paris", "categories": ["hotels"], "radius": 1000})
        self.assertEqual(response.status_code, 200)

    def test_search_keyword(self):
        response = self.app.post("/search_keyword", data={"keyword": "Eiffel Tower"})
        self.assertEqual(response.status_code, 302)

    def test_delete_account(self):
        response = self.app.post("/delete_account")
        self.assertEqual(response.status_code, 302)

    def test_show_search_history(self):
        response = self.app.get("/search_history")
        self.assertEqual(response.status_code, 302)

    def test_show_popular_searches(self):
        response = self.app.get("/popular_searches")
        self.assertEqual(response.status_code, 302)


class TestDatabase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.drop_all()

    def test_hash_password(self):
        password = "password123"
        hashed_password = hash_password(password)
        self.assertNotEqual(password, hashed_password)

    def test_save_history(self):
        with app.app_context():
            user = User(username="testuser", password=hash_password("password123"))
            db.session.add(user)
            db.session.commit()
            user_id = user.user_id
            results = [{"name": "Place 1", "location": {"formatted_address": "Address 1"}},
                       {"name": "Place 2", "location": {"formatted_address": "Address 2"}}]
            save_history(db.session, user_id, results)
            search_history = SearchHistory.query.filter_by(user_id=user_id).all()
            self.assertEqual(len(search_history), 2)
            self.assertEqual(search_history[0].place_name, "Place 1")
            self.assertEqual(search_history[0].address, "Address 1")
            self.assertEqual(search_history[1].place_name, "Place 2")
            self.assertEqual(search_history[1].address, "Address 2")

    def test_get_history(self):
        with app.app_context():
            user = User(username="testuser", password=hash_password("password123"))
            db.session.add(user)
            db.session.commit()
            user_id = user.user_id
            results = [{"name": "Place 1", "location": {"formatted_address": "Address 1"}},
                       {"name": "Place 2", "location": {"formatted_address": "Address 2"}}]
            save_history(db.session, user_id, results)
            search_history = get_history(db.session, user_id)
            self.assertEqual(len(search_history), 2)
            self.assertEqual(search_history[0][0], "Place 1")
            self.assertEqual(search_history[0][1], "Address 1")
            self.assertEqual(search_history[1][0], "Place 2")
            self.assertEqual(search_history[1][1], "Address 2")

    def test_get_top_searches(self):
        with app.app_context():
            user = User(username="testuser", password=hash_password("password123"))
            db.session.add(user)
            db.session.commit()
            user_id = user.user_id
            results = [{"name": "Place 1", "location": {"formatted_address": "Address 1"}},
                       {"name": "Place 2", "location": {"formatted_address": "Address 2"}},
                       {"name": "Place 1", "location": {"formatted_address": "Address 1"}}]
            save_history(db.session, user_id, results)
            most_popular_searches = get_top_searches(db.session, user_id)
            self.assertEqual(len(most_popular_searches), 2)
            self.assertEqual(most_popular_searches[0][0], "Place 1")
            self.assertEqual(most_popular_searches[0][1], "Address 1")
            self.assertEqual(most_popular_searches[0][2], 2)

    def test_search_history(self):
        with app.app_context():
            user = User(username="testuser", password=hash_password("password123"))
            db.session.add(user)
            db.session.commit()
            user_id = user.user_id
            results = [{"name": "Place 1", "location": {"formatted_address": "Address 1"}}, {"name": "Place 2", "location": {"formatted_address": "Address 2"}}, {"name": "Place A", "location": {"formatted_address": "Address A"}}]
            save_history(db.session, user_id, results)
            search_results = search_history(db.session, user_id, 'A')
            self.assertEqual(len(search_results), 3)


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
