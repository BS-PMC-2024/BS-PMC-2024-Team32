from flask_mail import Message
from app import mail, app

def send_contact_email(inquiry_data):
    subject = f"New Contact Inquiry from {inquiry_data['name']}"
    sender = app.config['MAIL_DEFAULT_SENDER']
    recipients = [app.config['CONTACT_EMAIL']]
    
    body = f"""
    New contact inquiry received:
    
    Name: {inquiry_data['name']}
    Email: {inquiry_data['email']}
    Phone: {inquiry_data['phone']}
    Organization: {inquiry_data['organization']}
    Role: {inquiry_data['role']}
    Preferred Contact: {inquiry_data['preferred_contact']}
    Best Time to Contact: {inquiry_data['best_time']}
    
    Message:
    {inquiry_data['message']}
    """
    
    msg = Message(subject, sender=sender, recipients=recipients, body=body)
    mail.send(msg)