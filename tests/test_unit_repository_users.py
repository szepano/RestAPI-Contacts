import unittest
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from contacts_api.database.models import User
from contacts_api.schemas import UserModel, UserDB
from contacts_api.repository.users import (
    get_user_by_email,
    create_user,
    update_token,
    confirmed_email,
    update_avatar
)

class TestUsers(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.example_user = UserModel(username='test_user',
                                      email='test@example.com',
                                      password='random',
                                      refresh_token='old_token')
        

    async def test_get_user_by_email_found(self):
        user = User(**self.example_user.dict())
        self.session.query().filter().first.return_value = user
        result = await get_user_by_email(email=self.example_user.email, db=self.session)
        self.assertEqual(result, user)

    async def test_get_user_by_email_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_user_by_email(email='', db=self.session)
        self.assertIsNone(result)

    async def test_create_user(self):
        user = User(**self.example_user.dict())
        self.session.add.return_value = None
        self.session.commit.return_value = None
        self.session.refresh.return_value = None
        self.session.query().filter().first.return_value = user

        result = await create_user(body=self.example_user, db=self.session)

        self.assertEqual(result.email, self.example_user.email)
        self.assertEqual(result.username, self.example_user.username)
        self.session.add.assert_called_once()
        self.session.commit.assert_called_once()
        self.session.refresh.assert_called_once()

    async def test_update_token(self):
        new_token = 'new_token'
        user = User(**self.example_user.dict())
        result = await update_token(user=user, token=new_token, db=self.session)

        self.assertEqual(user.refresh_token, new_token)
        self.assertIsNone(result)
        self.session.commit.assert_called_once()

    async def test_confirmed_email(self):
        user = User(**self.example_user.dict())
        self.session.query().filter().first.return_value = user
        result = await confirmed_email(email=self.example_user.email, db=self.session)
        self.assertEqual(user.confirmed, True)
        self.session.commit.assert_called_once()
        self.assertIsNone(result)

    async def test_update_avatar(self):
        user = User(**self.example_user.dict())
        self.session.query().filter().first.return_value = user
        url = 'test_url'
        result = await update_avatar(email=self.example_user.email, url=url, db=self.session)
        self.assertEqual(result, user)
        self.assertEqual(user.avatar, url)
        self.session.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()