import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv
from os import getenv

load_dotenv()

def send_set_password_email(to_email, subject, body):
    sender_email = getenv('GMAIL_USERNAME')
    password = getenv('GMAIL_SECRET_KEY')
    print(sender_email, password)
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, to_email, msg.as_string())

