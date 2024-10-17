from eventify import db  # Import from the correct app module

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    events = db.relationship('Event', backref='category', lazy=True)

# Schema for the Event model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    time = db.Column(db.String(8), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    featured = db.Column(db.Boolean, default=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    image_file = db.Column(db.String(120), nullable=True)

    # Keep the rsvps relationship here
    rsvps = db.relationship('RSVP', backref='event')  # This backref should stay

    def __repr__(self):
        return f"<Event {self.title} - {self.date}>"

# Schema for the RSVP model
class RSVP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    attending = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<RSVP {self.name} for Event {self.event.title}>"
