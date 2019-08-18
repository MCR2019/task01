from sqlalchemy.sql import func
from app import db, ma


class Email(db.Model):
    """
    Email table to store email addresses for usernames.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), db.ForeignKey('contact_store.username'))
    email_address = db.Column(db.String(32), nullable=False)


class EmailSchema(ma.ModelSchema):
    """
    Marshmallow schema for the email table, useful for serlialising table query results.
    """
    class Meta:
        model = Email


class ContactStore(db.Model):
    """
    This class defines the contact_store table in the db for storing contact details.
    """
    username = db.Column(db.String(32), primary_key=True)
    first_name = db.Column(db.String(32))
    last_name = db.Column(db.String(32))
    timestamp = db.Column(db.DateTime(timezone=True), server_default=func.now(), nullable=False)
    emails = db.relationship('Email', backref='contact_store', cascade='all')


class ContactStoreSchema(ma.ModelSchema):
    """
    Marshmallow schema for the contact_store table, useful for serlialising table query results.
    """
    emails = ma.Nested(EmailSchema, many=True, only=["email_address"])

    class Meta:
        model = ContactStore
