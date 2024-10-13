import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'any_secret_key')  # Ensure fallback works for dev
    SQLALCHEMY_DATABASE_URI = os.environ.get('DB_URL') or \
        'sqlite:///' + os.path.join(basedir, 'eventify.db')  # Ensure fallback to SQLite
    SQLALCHEMY_TRACK_MODIFICATIONS = False
