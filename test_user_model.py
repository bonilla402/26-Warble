"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        u1 = User.signup("John Doe", "jdoe@email.com", "123456", "mujpg.jpg")
        u2 = User.signup("Jane Smith", "jsmith@email.com", "654321", "None.jpg")
 
        db.session.commit()

        self.u1 = u1
        self.uid1 = u1.id

        self.u2 = u2
        self.uid2 = u2.id

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)

    #Login Tests
    def test_valid_login(self):
        user = User.authenticate(self.u1.username, "123456")
        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.uid1)
    
    def test_invalid_user(self):
        self.assertFalse(User.authenticate("somename", "123456"))

    def test_bad_password(self):
        self.assertFalse(User.authenticate(self.u1.username, "sdfsdfsd"))


    #Following Tests
    def test_user_follows(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        first_follower = self.u2.followers[0]
        self.assertEqual(first_follower.id, self.u1.id)

        first_following = self.u1.following[0]
        self.assertEqual(first_following.id, self.u2.id)

    def test_is_following(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))

    def test_is_followed_by(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))        


    # Signup

    def test_signup(self):
        u_test = User.signup("testerPRO", "tPro@email.com", "123456", None)
        db.session.commit()
        uid = u_test.id

        u_test = User.query.get(uid)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.username, "testerPRO")
        self.assertEqual(u_test.email, "tPro@email.com")


    def test_bad_username(self):
        invalid = User.signup(None, "tPro@email.com", "fsdfsdfs", None)

        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    
    def test_bad_password(self):
        with self.assertRaises(ValueError) as context:
            User.signup("testerPRO", "tPro@email.com", "", None)
        
