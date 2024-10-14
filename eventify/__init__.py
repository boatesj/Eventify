from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
from config import Config
from flask_mail import Mail
import os

# Check if env.py exists and load it (to set environment variables locally)
if os.path.exists("env.py"):
    import env  # This will set environment variables from env.py

# Initialize the app
app = Flask(__name__)

# Load environment variables from the Config class
app.config.from_object(Config)

# Initialize the database
db = SQLAlchemy(app)

# Initialize Flask-Migrate for handling migrations
migrate = Migrate(app, db)

# Initialize Flask extensions
mail = Mail(app)

# Custom filter to format datetime to 'dd-mm-yyyy'
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

# Import routes and models at the end to avoid circular imports
from eventify import routes, models
