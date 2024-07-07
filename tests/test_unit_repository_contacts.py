import unittest
from unittest.mock import MagicMock
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from contacts_api.database.models import Contact, User
from contacts_api.schemas import ContactModel, ContactUpdate
from contacts_api.repository.contacts import (
    get_contacts,
    get_contact,
    create_contact,
    remove_contact,
    update_contact,
    find_contact,
    get_birthdays
)
import sys

class TestContacts(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        contacts = [Contact(), Contact(), Contact()]
        self.session.query().filter().offset().limit().all.return_value = contacts
        result = await get_contacts(skip=0, limit=10, user=self.user, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_find_contact_found(self):
        contact = Contact(first_name='test')
        self.session.query().filter().all.return_value = [contact]
        result = await find_contact(query='test', user=self.user, db=self.session)
        self.assertIsNotNone(result)
        self.assertEqual(contact.first_name, result[0].first_name)

    async def test_find_contact_not_found(self):
        self.session.query().filter().all.return_value = None
        result = await find_contact(query='test', user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactModel(first_name='test',
                            last_name='contact',
                            email='test@example.com',
                            phone='123456789',
                            birth_date=datetime.today().date(),
                            )
        contact = Contact(**body.dict(), user_id=self.user.id)

        self.session.add.return_value = None
        self.session.commit.return_value = None
        self.session.refresh.return_value = None
        self.session.query().filter().all.return_value = contact

        result = await create_contact(body=body, user=self.user, db=self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.user_id, self.user.id)

    async def test_remove_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_update_contact_found(self):
        body = ContactModel(id=1,
                            first_name='test',
                            last_name='contact',
                            email='test@example.com',
                            phone='123456789',
                            birth_date=datetime.today().date(),
                            )
        contact = Contact(**body.dict(), user_id=self.user.id)

        updated_contact = ContactUpdate(
            first_name='updated',
            last_name='contact',
            email='updated@example.com',
            phone='123456789',
            birth_date=datetime.today().date()
            )

        self.session.query().filter().first.return_value = contact
        result = await update_contact(contact_id=1, body=updated_contact, user=self.user, db=self.session)
        self.assertEqual(result.first_name, updated_contact.first_name)
        self.assertEqual(result.email, updated_contact.email)
        self.session.commit.asser_called_once()

    async def test_update_contact_not_found(self):

        updated_contact = ContactModel(
            first_name='updated',
            last_name='contact',
            email='updated@example.com',
            phone='123456789',
            birth_date=datetime.today().date()
            )
        
        self.session.query().filter().first.return_value = None
        result = await update_contact(contact_id=1, body=updated_contact, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_remove_contact_found(self):
        contact = Contact()
        self.session.query().filter().first.return_value = contact
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertEqual(result, contact)

    async def test_remove_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await remove_contact(contact_id=1, user=self.user, db=self.session)
        self.assertIsNone(result)

    async def test_get_birthdays_found(self):
        body = ContactModel(id=1,
                            first_name='test',
                            last_name='contact',
                            email='test@example.com',
                            phone='123456789',
                            birth_date=(datetime.today() + timedelta(days=3)).date(),
                            )
        contact = Contact(**body.dict(), user_id=self.user.id)
        self.session.query().filter().all.return_value = [contact]
        result = await get_birthdays(user=self.user, db=self.session)
        self.assertIsNotNone(result)
        self.assertEqual(result, [contact])

    async def test_get_birthdays_not_found(self):
        self.session.query().filter().all.return_value = None
        result = await get_birthdays(user=self.user, db=self.session)
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()

    