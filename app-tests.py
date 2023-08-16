import unittest
from app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_home(self):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)

    def test_search_page(self):
        response = self.app.get("/search.html")
        self.assertEqual(response.status_code, 200)

    def test_search_location(self):
        response = self.app.post("/search", data={"search": "SE1 9DD", "categories": ["restaurant"], "radius": 1000})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"results", response.data)

    def test_login_handler(self):
        response = self.app.post("/login.html", data={"username": "newtestuser", "password": "newtestpass"})
        self.assertEqual(response.status_code, 302)
        self.assertIn(b"/account.html", response.data)

    def test_account(self):
        with self.app.session_transaction() as session:
            session["user_id"] = 1
            session["username"] = "testuser"
        response = self.app.get("/account.html")
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        with self.app.session_transaction() as session:
            session["user_id"] = 1
            session["username"] = "testuser"
        response = self.app.get("/logout")
        self.assertEqual(response.status_code, 302)
        self.assertIn(b"/", response.data)

    def test_search_keyword(self):
        with self.app.session_transaction() as session:
            session["user_id"] = 1
        response = self.app.post("/search_keyword", data={"keyword": "test"})
        self.assertEqual(response.status_code, 200)

    def test_show_search_history(self):
        with self.app.session_transaction() as session:
            session["user_id"] = 1
        response = self.app.get("/search_history")
        self.assertEqual(response.status_code, 200)

    def test_show_popular_searches(self):
        with self.app.session_transaction() as session:
            session["user_id"] = 1
        response = self.app.get("/popular_searches")
        self.assertEqual(response.status_code, 200)

    def test_register_new_user(self):
        response = self.app.post("/register.html", data={"username": "newtestuser", "password": "newtestpass"})
        self.assertEqual(response.status_code, 200)

    def test_register_existing_user(self):
        response = self.app.post("/register.html", data={"username": "existingtestuser", "password": "existingtestpass"})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Username already exists - try another", response.data)

    def test_delete_account_success(self):
        with self.app.session_transaction() as session:
            session["user_id"] = 1
        response = self.app.post("/delete_account")
        self.assertEqual(response.status_code, 200)


    def test_delete_account_failure(self):
        with self.app.session_transaction() as session:
            session["user_id"] = 99999
        response = self.app.post("/delete_account")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Failed to delete account", response.data)

if __name__ == "__main__":
    unittest.main()
