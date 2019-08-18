import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(BASE_DIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True

    # Celery config
    CELERY_BROKER_URL = 'redis://localhost:6379'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379'

    CELERYBEAT_SCHEDULE = {
        'create-random-contact-15s': {
            'task': 'app.tasks.create_random_contact',
            'schedule': timedelta(seconds=15)
        },
        'delete-contacts-older-60s': {
            'task': 'app.tasks.delete_contacts_older_than',
            'schedule': timedelta(seconds=60)
        }
    }
