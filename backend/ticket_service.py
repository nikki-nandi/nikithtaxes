import random
import string

from backend.database import SessionLocal
from backend.models import Ticket


def generate_ticket_id():

    prefix = "MTX"

    random_number = ''.join(random.choices(string.digits, k=5))

    return f"{prefix}-{random_number}"


def create_ticket(name, email, reason):

    db = SessionLocal()

    ticket_id = generate_ticket_id()

    ticket = Ticket(
        ticket_id=ticket_id,
        name=name,
        email=email,
        reason=reason
    )

    db.add(ticket)

    db.commit()

    db.close()

    return ticket_id


def get_ticket_status(ticket_id):

    db = SessionLocal()

    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()

    db.close()

    if ticket:
        return ticket.status

    return None