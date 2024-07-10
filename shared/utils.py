import threading

from django.core.mail import EmailMessage, send_mail
from conf.settings import EMAIL_HOST
from twilio.rest import Client
from dotenv import load_dotenv


def send_code_to_email(email, code):
    def send_in_thread():
        send_mail(
            from_email=EMAIL_HOST,
            recipient_list=[email],
            subject="Activation code",
            message=f"Your activation code is {code}"
        )

    thread = threading.Thread(target=send_in_thread)
    thread.start()

    return True

