"""Message View tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py

import os
from unittest import TestCase
from models import db, User, Message, Likes

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

class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        u1 = User.signup("John Doe", "jdoe@email.com", "123456", "mujpg.jpg") 
        db.session.commit()

        self.u = u1
        self.uid = u1.id
        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_user_model(self):
        """Does basic model work?"""

        m = Message(
            text="The warble!!!",
            user_id=self.uid
        )

        db.session.add(m)
        db.session.commit()

        # User should have 1 messages & no followers
        self.assertEqual(len(self.u.messages), 1)
        self.assertEqual(self.u.messages[0].id, m.id)


    def test_like_message(self):
        """test liking a message"""

        m = Message(
            id=55,
            text="The warble!!!",
            user_id=self.uid
        )

        db.session.add(m)
        db.session.commit()
        
        self.u.likes.append(m)

        db.session.commit()

        l = Likes.query.filter(Likes.user_id == self.uid).all()

        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].message_id, m.id)       