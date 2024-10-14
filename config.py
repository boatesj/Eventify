import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'any_secret_key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'eventify.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Mail Configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # Must be set in env.py or system environment
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')  # Must be set in env.py or system environment
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'aws.j.boates@gmail.com'

