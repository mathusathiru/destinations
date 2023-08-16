import unittest
from database import db, User, SearchHistory, hash_password, save_search_history, get_search_history, get_most_popular_searches, search_history
from app import app

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

    def test_save_search_history(self):
        with app.app_context():
            user = User(username="testuser", password=hash_password("password123"))
            db.session.add(user)
            db.session.commit()
            user_id = user.user_id
            results = [{"name": "Place 1", "location": {"formatted_address": "Address 1"}},
                       {"name": "Place 2", "location": {"formatted_address": "Address 2"}}]
            save_search_history(db.session, user_id, results)
            search_history = SearchHistory.query.filter_by(user_id=user_id).all()
            self.assertEqual(len(search_history), 2)
            self.assertEqual(search_history[0].place_name, "Place 1")
            self.assertEqual(search_history[0].address, "Address 1")
            self.assertEqual(search_history[1].place_name, "Place 2")
            self.assertEqual(search_history[1].address, "Address 2")

    def test_get_search_history(self):
        with app.app_context():
            user = User(username="testuser", password=hash_password("password123"))
            db.session.add(user)
            db.session.commit()
            user_id = user.user_id
            results = [{"name": "Place 1", "location": {"formatted_address": "Address 1"}},
                       {"name": "Place 2", "location": {"formatted_address": "Address 2"}}]
            save_search_history(db.session, user_id, results)
            search_history = get_search_history(db.session, user_id)
            self.assertEqual(len(search_history), 2)
            self.assertEqual(search_history[0][0], "Place 1")
            self.assertEqual(search_history[0][1], "Address 1")
            self.assertEqual(search_history[1][0], "Place 2")
            self.assertEqual(search_history[1][1], "Address 2")

    def test_get_most_popular_searches(self):
        with app.app_context():
            user = User(username="testuser", password=hash_password("password123"))
            db.session.add(user)
            db.session.commit()
            user_id = user.user_id
            results = [{"name": "Place 1", "location": {"formatted_address": "Address 1"}},
                       {"name": "Place 2", "location": {"formatted_address": "Address 2"}},
                       {"name": "Place 1", "location": {"formatted_address": "Address 1"}}]
            save_search_history(db.session, user_id, results)
            most_popular_searches = get_most_popular_searches(db.session, user_id)
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
            results = [{"name": "Place 1", "location": {"formatted_address": "Address 1"}},
                    {"name": "Place 2", "location": {"formatted_address": "Address 2"}},
                    {"name": "Place A", "location": {"formatted_address": "Address A"}}]
            save_search_history(db.session, user_id, results)
            search_results = search_history(db.session, user_id, 'A')
            self.assertEqual(len(search_results), 3)


if __name__ == '__main__':
    unittest.main()
