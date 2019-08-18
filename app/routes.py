from app import api
from app.views import Contact, ContactList


api.add_resource(ContactList, '/contacts')
api.add_resource(Contact, '/contacts/<string:username>')
