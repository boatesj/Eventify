from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime
import os

# Check if env.py exists and load it (to set environment variables locally)
if os.path.exists("env.py"):
    import env  # This will set environment variables from env.py

# Initialize the app
app = Flask(__name__)

# Load environment variables (ensure these are set by env.py or system)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'any_secret_key')  # Fallback for dev
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_URL', 'sqlite:///eventify.db')  # Default to SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Initialize Flask-Migrate for handling migrations
migrate = Migrate(app, db)

# Custom filter to format datetime to 'dd-mm-yyyy'
@app.template_filter('dateformat')
def dateformat(value, format='%d-%m-%Y'):
    if value is None:
        return ""
    
    # Check if the value is a string and attempt to parse it into a datetime object
    if isinstance(value, str):
        try:
            # First, attempt to parse a known format
            value = datetime.strptime(value, "%d-%m-%Y %H:%M")
        except ValueError:
            try:
                # Handle cases where the string is in 'YYYY-MM-DDTHH:MM' format
                value = datetime.strptime(value, "%Y-%m-%dT%H:%M")
            except ValueError:
                # Return the string as-is if parsing fails
                return value

    return value.strftime(format)


# Filter to format datetime for use in datetime-local input fields
@app.template_filter('datetime_local')
def datetime_local(value):
    """ Format the datetime for use in a datetime-local input """
    if value is None:
        return ""
    
    # If it's a string, try to parse it to a datetime object
    if isinstance(value, str):
        try:
            value = datetime.strptime(value, "%d-%m-%Y %H:%M")
        except ValueError:
            return value  # Return as-is if it's not parsable
    
    return value.strftime('%Y-%m-%dT%H:%M')


# Import routes at the end to avoid circular imports
from eventify import routes
