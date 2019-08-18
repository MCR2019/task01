from flask import request, jsonify, make_response
from flask_restful import Resource
from sqlalchemy import exc

from app import app, db
from app.models import ContactStore, ContactStoreSchema, Email, EmailSchema

contact_schema = ContactStoreSchema()
contacts_schema = ContactStoreSchema(many=True)
email_schema = EmailSchema()
emails_schema = EmailSchema(many=True)


class Contact(Resource):
    """
    Represents a single contact.
    """
    def get(self, username):
        """
        Get contact details for a given username.
        :param username: string representing the contact username in the db.
        :return: JSON serialised contact details.
        """
        contact = ContactStore.query.filter(ContactStore.username == username).first()
        result = contact_schema.dump(contact)

        if not contact:
            return make_response(jsonify(f"Username not found: {username}"), 404)
        else:
            return make_response(jsonify(result.data), 200)

    def delete(self, username):
        """
        Delete contact details for a given username.
        :param username: string representing the contact username in the db.
        :return: Confirmation of username deleted.
        """
        contact_to_delete = ContactStore.query.filter(ContactStore.username == username).first()
        if not contact_to_delete:
            return make_response(jsonify(f"Username not found: {username}"), 404)
        else:
            db.session.delete(contact_to_delete)
            db.session.commit()
            # Not a 204 as returning response body
            return make_response(jsonify(f"Deleted contact with username: {username}"), 200)

    def put(self, username):
        """
        Update contact details for a specified contact username.
        :return: Confirmation of updated username.
        """
        first_name = request.args.get('first_name')
        last_name = request.args.get('last_name')

        updated_contact = ContactStore.query.filter(ContactStore.username == username).first()

        if not updated_contact:
            return make_response(jsonify(f"Username not found: {username}"), 404)
        else:
            updated_contact.first_name = first_name
            updated_contact.last_name = last_name
            db.session.add(updated_contact)
            db.session.commit()
            return make_response(jsonify(f"Updated contact for username: {username}"), 200)


class ContactList(Resource):
    """
    Represents a collection of multiple contacts.
    """
    def get(self):
        """
        Get all contact details from the db.
        :return: JSON serialised list of contact details.
        """
        all_contacts = db.session.query(ContactStore).all()
        result = contacts_schema.dump(all_contacts)
        return jsonify(result.data)

    def post(self):
        """
        Create a new contact from the parameters; username, first_name, last_name.
        :return: JSON serlialised details of the newly created contact.
        """
        try:
            js_data = request.json
        except Exception as e:
            return make_response(jsonify(f"json data error: {str(e)}"), 400)

        if not js_data:
            return make_response(jsonify(f"No data received"), 400)

        username = js_data.get('username')
        first_name = js_data.get('first_name')
        last_name = js_data.get('last_name')
        emails = js_data.get('emails')

        try:
            new_contact = add_contact_to_db(username, first_name, last_name, emails)
        except exc.IntegrityError as e:
            return make_response(jsonify(f"DB integrity error, username may already exist: {username} - {str(e)}"), 409)

        result = contact_schema.dump(new_contact)
        return make_response(jsonify(result.data), 200)


def add_contact_to_db(username, first_name, last_name, emails):
    new_contact = ContactStore(username=username, first_name=first_name, last_name=last_name)

    email_model_list = []
    for email in emails:
        email_model_list.append(Email(username=username, email_address=email))

    new_contact.emails = email_model_list

    db.session.add(new_contact)
    db.session.commit()
    return new_contact


def delete_contacts_before(ts_cutoff):
    db.session.query(ContactStore).filter(ContactStore.timestamp <= ts_cutoff).delete()
    db.session.commit()
