from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pickle
import numpy as np
import os
from sentence_transformers import SentenceTransformer

from backend.ticket_service import create_ticket, get_ticket_status
from backend.email_utils import send_ticket_email
from backend.database import SessionLocal
from backend.models import Ticket

app = FastAPI()

# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------
# Lazy Load Models (IMPORTANT)
# -----------------------------
model = None
index = None
answers = None


def load_models():
    global model, index, answers

    if model is None:
        print("Loading SentenceTransformer model...")
        model = SentenceTransformer("all-MiniLM-L6-v2")

    if index is None:
        print("Loading FAISS model...")
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        MODEL_PATH = os.path.join(BASE_DIR, "model", "chatbot_model.pkl")

        with open(MODEL_PATH, "rb") as f:
            index, answers = pickle.load(f)


# -----------------------------
# Request Models
# -----------------------------
class ChatRequest(BaseModel):
    message: str


class TicketRequest(BaseModel):
    name: str
    email: str
    reason: str


# -----------------------------
# Home
# -----------------------------
@app.get("/")
def home():
    return {"message": "Mercury Tax Chatbot Running"}


# -----------------------------
# Chat API
# -----------------------------
@app.post("/chat")
def chat(request: ChatRequest):

    load_models()  # ✅ Load only when needed

    embedding = model.encode([request.message])
    D, I = index.search(np.array(embedding), 1)

    idx = I[0][0]
    answer = answers[idx]

    return {
        "answer": answer,
        "show_ticket_button": True
    }


# -----------------------------
# Raise Ticket
# -----------------------------
@app.post("/raise-ticket")
def raise_ticket(ticket: TicketRequest):

    ticket_id = create_ticket(ticket.name, ticket.email, ticket.reason)
    send_ticket_email(ticket_id, ticket.name, ticket.email, ticket.reason)

    return {
        "message": "Ticket created successfully",
        "ticket_id": ticket_id
    }


# -----------------------------
# Ticket Status
# -----------------------------
@app.get("/ticket-status/{ticket_id}")
def ticket_status(ticket_id: str):

    status = get_ticket_status(ticket_id)

    if status:
        return {"ticket_id": ticket_id, "status": status}

    return {"error": "Ticket not found"}


# -----------------------------
# Admin APIs
# -----------------------------
@app.get("/admin/tickets")
def get_all_tickets():
    db = SessionLocal()
    tickets = db.query(Ticket).all()
    db.close()
    return tickets


@app.get("/admin/ticket/{ticket_id}")
def get_ticket(ticket_id: str):
    db = SessionLocal()
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    db.close()

    if ticket:
        return ticket

    return {"error": "Ticket not found"}


@app.put("/admin/update-ticket/{ticket_id}")
def update_ticket(ticket_id: str, status: str):
    db = SessionLocal()
    ticket = db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()

    if ticket:
        ticket.status = status
        db.commit()
        db.close()
        return {"message": "Ticket updated successfully"}

    db.close()
    return {"error": "Ticket not found"}
