import sys
import os
from flask import request, redirect, url_for, flash, render_template, jsonify
from werkzeug.utils import secure_filename
from eventify import app, db
from eventify.models import Event, Category
from datetime import datetime
from eventify.models import RSVP  # Import the RSVP model
from eventify.email_utils import send_rsvp_confirmation
from flask_mail import Message
from eventify import mail
from datetime import datetime, timedelta
from flask_login import current_user
import json




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

  
    return render_template("events.html", upcoming_events=upcoming_events, past_events=past_events, featured_events=featured_events, user=current_user)


# Add event details
@app.route("/event/<int:event_id>", methods=["GET", "POST"])
def event_detail(event_id):
    event = Event.query.get_or_404(event_id)
    rsvps = RSVP.query.filter_by(event_id=event_id).all()  # Fetch RSVPs for this event

    
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

            # Parse the date and time strings using dd-mm-yyyy format for date and HH:MM for time
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
                print(f"File path: {file_path}")  # Log the file path
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                file.save(file_path)
                print(f"File {filename} saved successfully.")
            else:
                print("File upload failed or invalid file type.")

            # Create the event and save it to the database
            event = Event(
                title=title,
                description=description,
                date=event_date,  # Store date as datetime object
                time=event_time_raw,  # Store time as string (make sure it's passed here)
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
        try:
            # Extract date and time separately from the form
            event_date_raw = request.form.get("date")  # Expecting 'dd-mm-yyyy'
            event_time_raw = request.form.get("time")  # Expecting 'HH:MM'

            # Split and handle date and time separately
            day, month, year = map(int, event_date_raw.split('-'))
            hour, minute = map(int, event_time_raw.split(':'))

            # Create a datetime object and update event
            event.date = datetime(year, month, day, hour, minute)

            # Update other event details from the form
            event.title = request.form.get("title")
            event.description = request.form.get("description")
            event.location = request.form.get("location")
            event.category_id = request.form.get("category_id")
            event.featured = request.form.get("featured") == "1"  # Store as boolean

            # Handle file upload (if a new image is uploaded)
            file = request.files.get('image')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.static_folder, 'images', filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                file.save(file_path)
                event.image_file = filename  # Update the filename in the database

            # Commit the changes to the database
            db.session.commit()
            flash('Event updated successfully!', 'success')
            return redirect(url_for("home"))
        
        except Exception as e:
            db.session.rollback()
            flash(f"Error updating event: {str(e)}", 'error')
            return redirect(url_for("edit_event", event_id=event_id))

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

    

# Search for events by title, description, category, date range, and location
@app.route("/search", methods=["GET", "POST"])
def search():
    categories = Category.query.all()  # Fetch all categories for dropdown

    if request.method == "POST":
        # Get search term and strip extra spaces
        search_term = request.form.get("search_term", "").strip()
        search_query = f"%{search_term}%"

        # Get selected filters from the form
        selected_category = request.form.get("category_id")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        location = request.form.get("location", "").strip()  # Location-based search
        sort_by = request.form.get("sort_by")  # Sort by date or popularity

        # Build the base query for title and description search
        query = Event.query.filter(
            (Event.title.ilike(search_query)) | 
            (Event.description.ilike(search_query))
        )

        # Filter by category if selected
        if selected_category:
            query = query.filter(Event.category_id == selected_category)

        # Filter by location if provided
        if location:
            query = query.filter(Event.location.ilike(f"%{location}%"))

        # Filter by date range if provided
        if start_date:
            query = query.filter(Event.date >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            query = query.filter(Event.date <= datetime.strptime(end_date, '%Y-%m-%d'))

        # Sort results by date or popularity
        if sort_by == "date":
            query = query.order_by(Event.date.asc())
        elif sort_by == "popularity":
            # Assuming you track RSVPs, sort by the count of RSVPs
            query = query.outerjoin(RSVP).group_by(Event.id).order_by(db.func.count(RSVP.id).desc())

        # Execute the query to get matched events
        matched_events = query.all()

        # Get current date and time to split upcoming and past events
        now = datetime.now()
        upcoming_events = [event for event in matched_events if event.date >= now]
        past_events = [event for event in matched_events if event.date < now]

        # Render the events page with the filtered results
        return render_template(
            "events.html", 
            upcoming_events=upcoming_events, 
            past_events=past_events, 
            categories=categories,
            search_term=search_term, 
            selected_category=selected_category, 
            start_date=start_date, 
            end_date=end_date, 
            location=location,
            sort_by=sort_by
        )

    return redirect(url_for("home"))



# Create a new RSVP
@app.route("/rsvp/<int:event_id>", methods=["POST"])
def rsvp(event_id):
    event = Event.query.get_or_404(event_id)
    
    # Get form data
    name = request.form.get("name")
    email = request.form.get("email")
    
    # Check if attending checkbox is ticked (if checkbox is submitted)
    attending = request.form.get("attending") is not None

    # Check if an RSVP for this event and email already exists
    rsvp_entry = RSVP.query.filter_by(event_id=event_id, email=email).first()

    if rsvp_entry:
        # Update existing RSVP
        rsvp_entry.attending = attending
        rsvp_entry.name = name  # Update name in case of changes
    else:
        # Create a new RSVP entry
        rsvp_entry = RSVP(event_id=event.id, name=name, email=email, attending=attending)
        db.session.add(rsvp_entry)

    # Commit the changes
    db.session.commit()

    # Send confirmation email using the utility function
    if send_rsvp_confirmation(name, email, event):
        flash('Thank you for your RSVP! A confirmation email has been sent.', 'success')
    else:
        flash('RSVP submitted but failed to send confirmation email.', 'error')

    return redirect(url_for('event_detail', event_id=event.id))


@app.route("/admin_dashboard")
def admin_dashboard():
    events = Event.query.order_by(Event.date.desc()).all()  # Fetch all events ordered by date
    rsvp_counts = {event.id: RSVP.query.filter_by(event_id=event.id).count() for event in events}  # Count RSVPs per event
    total_events = len(events)
    total_rsvps = sum(rsvp_counts.values())
    
    return render_template("admin_dashboard.html", events=events, rsvp_counts=rsvp_counts, total_events=total_events, total_rsvps=total_rsvps)



