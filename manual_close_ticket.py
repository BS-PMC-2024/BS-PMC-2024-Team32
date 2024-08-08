import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import SupportTicket  # Adjust this import based on your project structure

# Use the same database URI as in your Flask app
DATABASE_URI = 'mysql+pymysql://root:your_password@db/mathgenius'  # Adjust as needed

engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

def close_ticket(ticket_id):
    ticket = session.query(SupportTicket).get(ticket_id)
    if ticket:
        print(f"Current status of ticket {ticket_id}: {ticket.status}")
        ticket.status = 'Closed'
        session.commit()
        print(f"Ticket {ticket_id} status changed to: {ticket.status}")
    else:
        print(f"No ticket found with ID {ticket_id}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python manual_close_ticket.py <ticket_id>")
        sys.exit(1)
    
    ticket_id = int(sys.argv[1])
    close_ticket(ticket_id)