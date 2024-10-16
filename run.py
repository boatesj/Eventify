import os
from eventify import app  # Assuming app is initialized in __init__.py

def str_to_bool(value):
    """ Convert string values to boolean """
    return value.lower() in ('true', '1', 't', 'y', 'yes')

if __name__ == "__main__":
    # Get the debug flag and convert it to a proper boolean
    debug_mode = os.environ.get("DEBUG", "True")  # Default to "True"
    debug_mode = str_to_bool(debug_mode)  # Convert to boolean

    app.run(
        host=os.environ.get("IP", "0.0.0.0"),
        port=int(os.environ.get("PORT", 5000)),
        debug=debug_mode  # Use the properly converted boolean
    )



