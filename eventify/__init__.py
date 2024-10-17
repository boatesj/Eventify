import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from flask_mail import Mail
from flask_login import current_user  # Import Flask-Login's current_user

# Check if env.py exists and load it (to set environment variables locally)
if os.path.exists("env.py"):
    import env  # noqa

# Initialize the app
app = Flask(__name__)

# Set the SECRET_KEY from environment variables
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

# Database setup: check if in development mode or production
if os.environ.get("DEVELOPMENT") == "True":
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URL")
else:
    uri = os.environ.get("DATABASE_URL")
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = uri

# Initialize the database and Flask-Migrate for migrations
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Initialize Flask-Mail
mail = Mail(app)

# Custom filter to format datetime to 'dd-mm-yyyy' (U.K. format)
@app.template_filter('dateformat')
def dateformat(value, format='%d-%m-%Y'):
    if value is None:
        return ""
    
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, "%d-%m-%Y %H:%M")
        except ValueError:
            try:
                value = datetime.strptime(value, "%Y-%m-%dT%H:%M")
            except ValueError:
                return value

    return value.strftime(format)

# Filter to format datetime for use in datetime-local input fields
@app.template_filter('datetime_local')
def datetime_local(value):
    """ Format the datetime for use in a datetime-local input """
    if value is None:
        return ""
    
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, "%d-%m-%Y %H:%M")
        except ValueError:
            return value
    
    return value.strftime('%Y-%m-%dT%H:%M')

# Inject current_user globally into all templates
@app.context_processor
def inject_user():
    return dict(user=current_user)

# Import routes and models at the end to avoid circular imports
from eventify import routes  # noqa
from eventify import models  # noqa
