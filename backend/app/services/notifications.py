import os
import smtplib
from email.message import EmailMessage
from pathlib import Path


def send_notification(app, recipient, subject, body):
    host = app.config.get("SMTP_HOST", "")
    if host:
        message = EmailMessage()
        message["From"] = app.config["SMTP_FROM"]
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)
        with smtplib.SMTP(host, app.config["SMTP_PORT"]) as server:
            server.starttls()
            if app.config["SMTP_USERNAME"]:
                server.login(app.config["SMTP_USERNAME"], app.config["SMTP_PASSWORD"])
            server.send_message(message)
        return "email"
    path = Path(app.instance_path) / "notifications.log"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(f"TO={recipient}\nSUBJECT={subject}\n{body}\n---\n")
    return "log"
