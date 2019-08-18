"""
To run unit tests execute 'python testapi.py'.
"""
import os
import unittest
from json import loads

from app.constants import JSON_HEADER
from app import app, db
from app.models import ContactStore, Email

TEST_DB = 'test.db'

TEST_CONTACT_01 = {'username': 'testUsername01',
                   'first_name': 'myFirstName',
                   'last_name': 'myLastName',
                   'emails': ['myEmail01@email.com', 'myEmail02@email.com']
                   }
TEST_CONTACT_02 = {'username': 'testUsername02',
                   'first_name': 'myFirstName',
                   'last_name': 'myLastName',
                   'emails': ['myEmail01@email.com', 'myEmail02@email.com']
                   }


def generic_test_setup(test_case):
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['DEBUG'] = False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
                                            os.path.join(app.config['BASE_DIR'], TEST_DB)
    test_case.app = app.test_client()
    db.drop_all()
    db.create_all()

    # Insert test contact with email
    new_contact = ContactStore(username=TEST_CONTACT_01.get('username'),
                               first_name=TEST_CONTACT_01.get('first_name'),
                               last_name=TEST_CONTACT_01.get('last_name')
                               )

    email_model_list = []
    for email in TEST_CONTACT_01.get('emails'):
        email_model_list.append(
            Email(username=TEST_CONTACT_01.get('username'), email_address=email)
        )

    new_contact.emails = email_model_list

    db.session.add(new_contact)
    db.session.commit()


class ContactTests(unittest.TestCase):

    def setUp(self):
        generic_test_setup(self)

    def tearDown(self):
        pass

    # Retrieve contact by username tests
    def test_get_contact_with_username_exists(self):
        response = self.app.get(f"/contacts/{TEST_CONTACT_01.get('username')}")
        self.assertEqual(response.status_code, 200)

        py_response = loads(response.data)
        self.assertEqual(py_response.get('username'), TEST_CONTACT_01.get('username'))
        self.assertEqual(py_response.get('first_name'), TEST_CONTACT_01.get('first_name'))
        self.assertEqual(py_response.get('last_name'), TEST_CONTACT_01.get('last_name'))

        email_list = [x.get('email_address') for x in py_response.get('emails')]
        self.assertEqual(email_list, TEST_CONTACT_01.get('emails'))

    def test_get_contact_with_username_unknown(self):
        response = self.app.get(f"/contacts/unknownusername")
        self.assertEqual(response.status_code, 404)
        self.assertIn(f"Username not found: unknownusername", str(response.data))

    # Delete contact by username tests
    def test_delete_contact_with_username_exists(self):
        response = self.app.delete(f"/contacts/{TEST_CONTACT_01.get('username')}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            f"Deleted contact with username: {TEST_CONTACT_01.get('username')}",
            str(response.data)
        )

    def test_delete_contact_with_username_unknown(self):
        response = self.app.delete(f"/contacts/unknownusername")
        self.assertEqual(response.status_code, 404)
        self.assertIn(f"Username not found: unknownusername", str(response.data))

    # Update contact by username tests
    def test_update_contact_with_username_exists(self):
        response = self.app.put(f"/contacts/{TEST_CONTACT_01.get('username')}")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            f"Updated contact for username: {TEST_CONTACT_01.get('username')}",
            str(response.data)
        )

    def test_update_contact_with_username_unknown(self):
        response = self.app.put(f"/contacts/unknownusername")
        self.assertEqual(response.status_code, 404)
        self.assertIn(f"Username not found: unknownusername", str(response.data))


class ContactListTests(unittest.TestCase):

    def setUp(self):
        generic_test_setup(self)

    def tearDown(self):
        pass

    # Retrieve all contacts tests
    def test_get_all_contacts(self):
        response = self.app.get('/contacts')
        self.assertEqual(response.status_code, 200)

        py_response = loads(response.data)
        self.assertEqual(len(py_response), 1)
        self.assertEqual(py_response[0].get('username'), TEST_CONTACT_01.get('username'))
        self.assertEqual(py_response[0].get('first_name'), TEST_CONTACT_01.get('first_name'))
        self.assertEqual(py_response[0].get('last_name'), TEST_CONTACT_01.get('last_name'))

    # Create new contact tests
    def test_create_new_contact(self):
        response = self.app.post('/contacts',
                                 headers=JSON_HEADER,
                                 json=TEST_CONTACT_02
                                 )
        self.assertEqual(response.status_code, 200)

        py_response = loads(response.data)
        self.assertEqual(py_response.get('username'), TEST_CONTACT_02.get('username'))
        self.assertEqual(py_response.get('first_name'), TEST_CONTACT_02.get('first_name'))
        self.assertEqual(py_response.get('last_name'), TEST_CONTACT_02.get('last_name'))

        email_list = [x.get('email_address') for x in py_response.get('emails')]
        self.assertEqual(email_list, TEST_CONTACT_02.get('emails'))

    def test_create_new_contact_already_exists(self):
        response = self.app.post('/contacts',
                                 headers=JSON_HEADER,
                                 json=TEST_CONTACT_01
                                 )
        self.assertEqual(response.status_code, 409)
        self.assertIn(f"DB integrity error, username may already exist: {TEST_CONTACT_01.get('username')}",
                      str(response.data))


if __name__ == '__main__':
    unittest.main()
