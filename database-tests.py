from database import db, User, SearchHistory, hash_password, save_history, get_history, get_top_searches, delete_account
import unittest
from app import app


class TestDatabase(unittest.TestCase):
    def setUp(self):
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
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
            results = [{"name": "Eiffel Tower", "location": {"formatted_address": "Champ de Mars, 5 Avenue Anatole France, 75007 Paris, France"}}]
            save_history(db.session, user_id, results)
            search_history = SearchHistory.query.filter_by(user_id=user_id).first()
            self.assertEqual(search_history.place_name, "Eiffel Tower")
            self.assertEqual(search_history.address, "Champ de Mars, 5 Avenue Anatole France, 75007 Paris, France")

    def test_get_history(self):
        with app.app_context():
            user = User(username="testuser", password=hash_password("password123"))
            db.session.add(user)
            db.session.commit()
            user_id = user.user_id
            results = [{"name": "Eiffel Tower", "location": {"formatted_address": "Champ de Mars, 5 Avenue Anatole France, 75007 Paris, France"}}]
            save_history(db.session, user_id, results)
            search_history = get_history(db.session, user_id)
            self.assertEqual(len(search_history), 1)
            self.assertEqual(search_history[0].place_name, "Eiffel Tower")
            self.assertEqual(search_history[0].address, "Champ de Mars, 5 Avenue Anatole France, 75007 Paris, France")

    def test_get_top_searches(self):
        with app.app_context():
            user = User(username="testuser", password=hash_password("password123"))
            db.session.add(user)
            db.session.commit()
            user_id = user.user_id
            results = [{"name": "Eiffel Tower", "location": {"formatted_address": "Champ de Mars, 5 Avenue Anatole France, 75007 Paris, France"}}, {"name": "Eiffel Tower", "location": {"formatted_address": "Champ de Mars, 5 Avenue Anatole France, 75007 Paris, France"}}, {"name": "Louvre Museum", "location": {"formatted_address": "Rue de Rivoli, 75001 Paris, France"}}]
            save_history(db.session, user_id, results)
            most_popular_searches = get_top_searches(db.session, user_id)
            self.assertEqual(len(most_popular_searches), 2)
            self.assertEqual(most_popular_searches[0].place_name, "Eiffel Tower")
            self.assertEqual(most_popular_searches[0].search_count, 2)

    def test_search_history(self):
        with app.app_context():
            user = User(username="testuser", password=hash_password("password123"))
            db.session.add(user)
            db.session.commit()
            user_id = user.user_id
            results = [{"name": "Eiffel Tower", "location": {"formatted_address": "Champ de Mars, 5 Avenue Anatole France, 75007 Paris, France"}}, {"name": "Louvre Museum", "location": {"formatted_address": "Rue de Rivoli, 75001 Paris, France"}}]

    def test_delete_account(self):
        with app.app_context():
            user = User(username="testuser", password=hash_password("password123"))
            db.session.add(user)
            db.session.commit()
            user_id = user.user_id
            results = [{"name": "Eiffel Tower", "location": {"formatted_address": "Champ de Mars, 5 Avenue Anatole France, 75007 Paris, France"}}]
            save_history(db.session, user_id, results)
            search_history = get_history(db.session, user_id)
            self.assertEqual(len(search_history), 1)
            self.assertEqual(search_history[0].place_name, "Eiffel Tower")
            self.assertEqual(search_history[0].address, "Champ de Mars, 5 Avenue Anatole France, 75007 Paris, France")

            delete_account(db.session, user_id)

            search_history = get_history(db.session, user_id)
            self.assertEqual(len(search_history), 0)

            user = db.session.get(User, user_id)
            self.assertIsNone(user)


if __name__ == '__main__':
    unittest.main()
