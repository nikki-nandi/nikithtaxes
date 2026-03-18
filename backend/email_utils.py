import smtplib
from email.mime.text import MIMEText
import os

def send_ticket_email(ticket_id, name, email, reason):

    try:
        sender = os.getenv("EMAIL_USER")
        password = os.getenv("EMAIL_PASS")

        message = f"""
New Support Ticket

Ticket ID: {ticket_id}
Name: {name}
Email: {email}

Issue:
{reason}
"""

        msg = MIMEText(message)
        msg["Subject"] = "New Ticket"
        msg["From"] = sender
        msg["To"] = sender

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)

        server.sendmail(sender, sender, msg.as_string())
        server.quit()

    except Exception as e:
        print("EMAIL ERROR:", e)
