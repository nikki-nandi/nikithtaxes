from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import pandas as pd
from difflib import get_close_matches

from backend.database import engine, SessionLocal
from backend.models import Base, Ticket
from backend.ticket_service import create_ticket, get_ticket_status
from backend.email_utils import send_ticket_email

from openai import OpenAI

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load dataset
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "mercury_tax_full_chatbot_dataset.csv")

data = pd.read_csv(DATA_PATH)

questions = data["question"].tolist()
answers = data["answer"].tolist()

# OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Search
def get_best_match(user_input):
    matches = get_close_matches(user_input, questions, n=1, cutoff=0.5)

    if matches:
        index = questions.index(matches[0])
        return answers[index]

    return None

# Models
class ChatRequest(BaseModel):
    message: str

class TicketRequest(BaseModel):
    name: str
    email: str
    reason: str

# Home
@app.get("/")
def home():
    return {"message": "Backend Running 🚀"}

# Chat
@app.post("/chat")
def chat(request: ChatRequest):

    match = get_best_match(request.message)

    if match:
        return {"answer": match, "show_ticket_button": True}

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a tax assistant."},
                {"role": "user", "content": request.message}
            ]
        )

        return {
            "answer": response.choices[0].message.content,
            "show_ticket_button": True
        }

    except:
        return {"answer": "Please raise a ticket."}

# Raise Ticket
@app.post("/raise-ticket")
def raise_ticket(ticket: TicketRequest):

    ticket_id = create_ticket(ticket.name, ticket.email, ticket.reason)

    send_ticket_email(ticket_id, ticket.name, ticket.email, ticket.reason)

    return {
        "message": "Ticket created",
        "ticket_id": ticket_id
    }

# Status
@app.get("/ticket-status/{ticket_id}")
def status(ticket_id: str):
    status = get_ticket_status(ticket_id)

    if status:
        return {"ticket_id": ticket_id, "status": status}

    return {"error": "Not found"}

# Admin
@app.get("/admin/tickets")
def admin():
    db = SessionLocal()
    tickets = db.query(Ticket).all()
    db.close()
    return tickets
