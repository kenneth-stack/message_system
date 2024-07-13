## Messaging System with RabbitMQ/Celery and Python Application behind Nginx

## Objective: Deploy a Python application behind Nginx that interacts with RabbitMQ/Celery for email sending and logging functionality.

## 1. Local Setup

### 1.1 Install RabbitMQ

1. Install Erlang (RabbitMQ dependency):
    
    ```
    sudo apt update
    sudo apt install erlang
    ```
    
2. Install RabbitMQ:
    
    ```
    sudo apt install rabbitmq-server
    ```
    
3. Start RabbitMQ service:
    
    ```
    sudo systemctl start rabbitmq-server

    ```
    

### 1.2 Install Celery and Flask

Install Celery using pip:

```
pip install celery
```
Install Flask using pip

```
pip install celery
```

### 1.3 Set up Python Application

Create a new Python file, e.g., `app.py`:

```python
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
```

## 2. Nginx Configuration

1. Install Nginx:
    
    ```
    sudo apt install nginx
    ```
    
2. Create a new Nginx configuration file:
    
    ```
    sudo nano /etc/nginx/sites-available/ngnix.conf
    ```
    
3. Add the following configuration:
    
    ```
    server {
        listen 80;
        server_name yourdomain.com;
    
        location / {
            proxy_pass http://127.0.0.1:5000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
    ```
    
4. Enable the site and restart Nginx:
    
    ```
    sudo ln -s /etc/nginx/sites-available/nginx.conf /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl restart nginx
    ```
    

## 3. Expose Endpoint with ngrok

1. Install ngrok:
    
    ```
    sudo snap install ngrok
    ```
    
2. Start ngrok:
    
    ```
    ngrok http 5000
    ```
    
3. Note the ngrok URL provided for your endpoint.

## 4. Testing

1. Start your Flask application:
    
    ```
    python app.py
    ```
    
2. In another terminal, start a Celery worker:
    
    ```
    celery -A app.celery worker --loglevel=info
    ```
    
3. Test the endpoints using the ngrok URL:
    - Send email: `http://<ngrok-url>/?sendmail=example@example.com`
    - Log time: `http://<ngrok-url>/?talktome`

Hope you enjoyed it