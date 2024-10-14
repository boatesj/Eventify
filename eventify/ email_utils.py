print("email_utils imported")


from flask_mail import Message
from eventify import mail

def send_rsvp_confirmation(name, email, event):
    try:
        msg = Message('RSVP Confirmation', 
                      sender='aws.j.boates@gmail.com',  # Replace with your email
                      recipients=[email])
        msg.body = f"Hello {name},\n\nThank you for your RSVP to the event: {event.title}.\n" \
                   f"Date: {event.date.strftime('%d %B, %Y')}\nLocation: {event.location}\n" \
                   f"Looking forward to your attendance!\n\nBest Regards,\nEventify Team"
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        return False
