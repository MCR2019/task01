from datetime import timedelta, datetime as dt
from string import digits, ascii_letters
from random import choice

from app import celery
from app.views import add_contact_to_db, delete_contacts_before


def random_string(length):
    """
    Return random ascii string of length characters long.
    """
    return ''.join([choice(ascii_letters + digits) for n in range(length)])


@celery.task()
def create_random_contact():
    """
    Create a random contact and add it to the db.
    """
    username = random_string(10)
    first_name = random_string(10)
    last_name = random_string(10)

    emails = [random_string(8) + '@email.com', random_string(8) + '@email.com']

    add_contact_to_db(username, first_name, last_name, emails)


@celery.task()
def delete_contacts_older_than(seconds=60):
    """
    Delete contacts with a timestamp older than now minus seconds.
    """
    ts_cutoff = dt.utcnow() - timedelta(seconds=seconds)
    delete_contacts_before(ts_cutoff)
