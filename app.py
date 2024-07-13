from flask import Flask, request
from celery import Celery
import smtplib
from email.mime.text import MIMEText
import logging
from datetime import datetime
import os

# Create the Flask app
app = Flask(__name__)

# Create the Celery app with RabbitMQ as the broker
celery = Celery(app.name, broker='pyamqp://guest:guest@localhost//')  # Update this if needed


# Ensure the log directory exists and configure logging
log_dir = '/var/log'
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, 'messaging_system.log')
logging.basicConfig(filename=log_path, level=logging.INFO)


# Set sensitive information directly
SENDER_EMAIL = 'yourmail@example.com'
SENDER_PASSWORD = 'your password'

@celery.task
def send_email(recipient):
    sender = SENDER_EMAIL
    password = SENDER_PASSWORD
    subject = "Test Email"
    body = "This is a test email sent from the messaging system."
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipient, msg.as_string())
        logging.info(f"Email sent to {recipient} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

@celery.task
def log_current_time():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    logging.info(f"Talktome request received at {current_time}")

@app.route('/')
def handle_request():
    if 'sendmail' in request.args:
        recipient = request.args.get('sendmail')
        send_email.delay(recipient)
        return f"Email queued for sending to {recipient}"
    elif 'talktome' in request.args:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_current_time.delay()
        return f"Current time logged: {current_time}"
    else:
        return "Invalid request. Use ?sendmail or ?talktome parameter."

if __name__ == '__main__':
    app.run(debug=True)