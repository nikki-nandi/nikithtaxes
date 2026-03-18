from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True)
    ticket_id = Column(String, unique=True)
    name = Column(String)
    email = Column(String)
    reason = Column(String)
    status = Column(String, default="Open")
