import smtplib
from email.mime.text import MIMEText


def send_ticket_email(ticket_id, name, email, reason):

    message = f"""
New Mercury Tax Support Ticket

Ticket ID: {ticket_id}

Name: {name}
Email: {email}

Issue:
{reason}
"""

    msg = MIMEText(message)

    msg["Subject"] = "Mercury Tax Support Ticket"
    msg["From"] = "yourgmail@gmail.com"
    msg["To"] = "nikithnandi2004@gmail.com"

    server = smtplib.SMTP("smtp.gmail.com",587)
    server.starttls()

    server.login("nikithnandi2004@gmail.com","qsie eaxy jzwr szau")


    server.sendmail(msg["From"], msg["To"], msg.as_string())

    server.quit()
















