"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_user_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows
from bs4 import BeautifulSoup

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        self.u1 = User.signup("abc", "test1@test.com", "password", None)
        self.u2 = User.signup("efg", "test2@test.com", "password", None)
        self.u3 = User.signup("hij", "test3@test.com", "password", None)
        self.u4 = User.signup("testing", "test4@test.com", "password", None)

        db.session.commit()

        self.testuser_id = self.testuser.id
        self.u1_id = self.u1.id
        self.u2_id = self.u2.id
        self.u3_id = self.u3.id
        self.u4_id = self.u4.id


    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_users_all(self):
        with self.client as c:
            resp = c.get("/users")

            self.assertIn("@testuser", str(resp.data))
            self.assertIn("@abc", str(resp.data))
            self.assertIn("@efg", str(resp.data))
            self.assertIn("@hij", str(resp.data))
            self.assertIn("@testing", str(resp.data))
            

    def test_user_show(self):
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get(f"/users/{self.testuser_id}")

            self.assertEqual(resp.status_code, 200)


    def test_add_like(self):
        m = Message(text="My Warble", user_id=self.u1_id)
        db.session.add(m)
        db.session.commit()

        print(f"Message Id: {m.id}")
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f"/users/add_like/{m.id}", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            likes = Likes.query.filter(Likes.message_id==m.id).all()
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].user_id, self.testuser_id)

    def test_add_like_no_session(self):
        m = Message(text="My Warble", user_id=self.u1_id)
        db.session.add(m)
        db.session.commit()

        print(f"Message Id: {m.id}")
        with self.client as c:

            resp = c.post(f"/users/add_like/{m.id}", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            self.assertIn("Access unauthorized", str(resp.data))


    def test_show_followers(self):

        f1 = Follows(user_being_followed_id=self.u1_id, user_following_id=self.testuser_id)

        db.session.add_all([f1])
        db.session.commit()
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser_id

            resp = c.get(f"/users/{self.u1_id}/followers")

            self.assertIn("@testuser", str(resp.data))
            