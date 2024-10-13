import os
from flask import request, redirect, url_for, flash, render_template
from werkzeug.utils import secure_filename
from eventify import app, db
from eventify.models import Event, Category
from datetime import datetime
from eventify.models import RSVP  # Import the RSVP model


# Allowed image extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Home page showing list of all upcoming and past events
@app.route("/")
def home():
    sort_by = request.args.get("sort_by", "date")  # Default sort by date
    order = request.args.get("order", "asc")  # Default order ascending

    now = datetime.now()

    featured_events = Event.query.filter_by(featured=True).order_by(Event.date.asc()).all()
    
    if sort_by == "date":
        if order == "asc":
            upcoming_events = Event.query.filter(Event.date >= now).order_by(Event.date.asc()).all()
            past_events = Event.query.filter(Event.date < now).order_by(Event.date.asc()).all()
        else:
            upcoming_events = Event.query.filter(Event.date >= now).order_by(Event.date.desc()).all()
            past_events = Event.query.filter(Event.date < now).order_by(Event.date.desc()).all()

    return render_template("events.html", upcoming_events=upcoming_events, past_events=past_events, featured_events=featured_events)


# Add event details
@app.route("/event/<int:event_id>", methods=["GET", "POST"])
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)

    # Fetch all RSVPs for this event to display on the event page
    rsvps = RSVP.query.filter_by(event_id=event_id).all()

    if request.method == "POST":
        try:
            # Debugging: Log the form data
            print(f"Form Submitted: {request.form}")

            # Handle RSVP form submission
            name = request.form.get("name")
            email = request.form.get("email")
            attending = request.form.get("attending") == "1" if request.form.get("attending") else False

            # Debugging: Log the RSVP details
            print(f"RSVP Details - Name: {name}, Email: {email}, Attending: {attending}")

            # Check if an RSVP for this event and email already exists
            existing_rsvp = RSVP.query.filter_by(event_id=event_id, email=email).first()

            if existing_rsvp:
                # Debugging: Log existing RSVP update
                print(f"Updating existing RSVP for {email}")

                # If RSVP exists, update it
                existing_rsvp.attending = attending
                existing_rsvp.name = name  # Update name in case the user changes it
                db.session.commit()
                flash(f"RSVP updated successfully for {email}!", "success")
            else:
                # Debugging: Log new RSVP creation
                print(f"Creating new RSVP for {email}")

                # Create a new RSVP entry
                rsvp_entry = RSVP(event_id=event_id, name=name, email=email, attending=attending)
                db.session.add(rsvp_entry)
                db.session.commit()
                flash(f"RSVP submitted successfully for {email}!", "success")

            # Redirect to avoid form re-submission on refresh
            return redirect(url_for("event_detail", event_id=event_id))

        except Exception as e:
            db.session.rollback()  # Roll back any changes in case of an error
            flash(f"Error submitting RSVP: {str(e)}", "error")
            return redirect(url_for("event_detail", event_id=event_id))

    # Pass the RSVPs to the template for display
    return render_template("event_detail.html", event=event, rsvps=rsvps)



# Create a new event
@app.route("/add_event", methods=["GET", "POST"])
def add_event():
    categories = Category.query.all()  # Fetch all categories
    if request.method == "POST":
        try:
            # Extract event details from the form
            title = request.form.get("title")
            description = request.form.get("description")
            event_date_raw = request.form.get("date")  # Expecting 'dd-mm-yyyy'
            event_time_raw = request.form.get("time")  # Expecting 'HH:MM'
            location = request.form.get("location")
            category_id = request.form.get("category_id")
            featured = request.form.get("featured") == "1"  # Store as boolean

            # Debugging: Log form data for troubleshooting
            print("Form Data:", request.form)
            print("Selected Date:", event_date_raw)
            print("Selected Time:", event_time_raw)

            # Parse the date and time strings
            day, month, year = map(int, event_date_raw.split('-'))
            hour, minute = map(int, event_time_raw.split(':'))

            # Create a datetime object for the event date and time
            event_date = datetime(year, month, day, hour, minute)

            # Handle file upload
            file = request.files.get('image')
            filename = None
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.static_folder, 'images', filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                file.save(file_path)

            # Create the event and save it to the database
            event = Event(
                title=title,
                description=description,
                date=event_date,  # Store date as datetime object
                time=event_time_raw,  # Store time as string
                location=location,
                category_id=category_id,
                featured=featured,
                image_file=filename  # Store the filename in the database
            )

            db.session.add(event)
            db.session.commit()
            flash('Event added successfully!', 'success')
            return redirect(url_for('home'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error adding event: {str(e)}', 'error')
            return redirect(url_for('add_event'))

    return render_template("add_event.html", categories=categories)





# Edit an existing event
@app.route("/edit_event/<int:event_id>", methods=["GET", "POST"])
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    categories = Category.query.all()  # Fetch categories for the dropdown
    
    if request.method == "POST":
        # Handle file upload
        file = request.files.get('image')  # Get the uploaded file
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.static_folder, 'images', filename)  # Update this path

            # Ensure the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Save the file
            file.save(file_path)
            event.image_file = filename  # Update the filename in the database

        # Get the other event details from the form
        event.title = request.form.get("title")  # Update title
        event.description = request.form.get("description")  # Update description
        
        # Parse the date and time
        event_date_raw = request.form.get("date")  # Expecting 'dd-mm-yyyy'
        event_time_raw = request.form.get("time")  # Expecting 'HH:MM'

        # Split the date string to get day, month, year
        day, month, year = map(int, event_date_raw.split('-'))
        hour, minute = map(int, event_time_raw.split(':'))

        # Create a datetime object and update event date
        event.date = datetime(year, month, day, hour, minute)

        event.location = request.form.get("location")  # Update location
        event.category_id = request.form.get("category_id")  # Update category
        event.featured = request.form.get("featured") == "1"  # Update featured status
        
        # Commit changes to the database
        db.session.commit()
        return redirect(url_for("home"))

    # Format the date and time for the form
    formatted_date = event.date.strftime('%d-%m-%Y')
    formatted_time = event.date.strftime('%H:%M')
    return render_template("edit_event.html", event=event, categories=categories, formatted_date=formatted_date, formatted_time=formatted_time)


# Delete an event
@app.route("/delete_event/<int:event_id>")
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for("home"))

# Create a new category and display existing categories
@app.route("/add_category", methods=["GET", "POST"])
def add_category():
    categories = Category.query.all()  # Fetch all categories to display

    if request.method == "POST":
        category_name = request.form.get("name").strip()  # Get and trim the category name
        
        # Check if the category name already exists
        existing_category = Category.query.filter_by(name=category_name).first()
        
        if existing_category:
            # If the category already exists, flash a message to the user
            flash(f'Category "{category_name}" already exists.', 'error')
            return redirect(url_for("add_category"))

        if category_name:
            # Only add the category if it's not empty and doesn't already exist
            new_category = Category(name=category_name)
            db.session.add(new_category)
            db.session.commit()
            flash(f'Category "{category_name}" added successfully!', 'success')
            return redirect(url_for("home"))  # Redirect to home after adding the category

    return render_template("add_category.html", categories=categories)

# Search for events by title or description
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        search_term = request.form.get("search_term").strip()  # Strip any extra spaces
        search_query = f"%{search_term}%"

        # Filter events by title or description that match the search term
        matched_events = Event.query.filter(
            (Event.title.ilike(search_query)) | 
            (Event.description.ilike(search_query))
        ).all()

        # Get the current date and time
        now = datetime.now()

        # Separate the matched events into upcoming and past
        upcoming_events = [event for event in matched_events if event.date >= now]
        past_events = [event for event in matched_events if event.date < now]

        # Render the events page with the filtered results
        return render_template("events.html", upcoming_events=upcoming_events, past_events=past_events)

    return redirect(url_for("home"))


# Create a new RSVP
@app.route("/rsvp/<int:event_id>", methods=["POST"])
def rsvp(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Get form data
    name = request.form.get("name")
    email = request.form.get("email")
    attending = request.form.get("attending") == "1"  # Check if the user is attending

    # Create an RSVP instance
    rsvp_entry = RSVP(event_id=event.id, name=name, email=email, attending=attending)
    db.session.add(rsvp_entry)
    db.session.commit()

    flash('Thank you for your RSVP!', 'success')
    return redirect(url_for('event_detail', event_id=event.id))
