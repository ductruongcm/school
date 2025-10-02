from celery_app import celery
from app.utils import send_set_password_email

@celery.task
def send_email_task(to, subject, body):
    return send_set_password_email(to, subject, body)