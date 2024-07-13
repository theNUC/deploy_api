import threading

from django.core.mail import EmailMessage, send_mail
from conf.settings import EMAIL_HOST
from twilio.rest import Client
from decouple import config


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


def send_code_to_phone(phone_number, code):
    def send_in_thread():
        account_sid = config('TWILIO_ID')
        auth_token = config('TWILIO_KEY')
        client = Client(account_sid, auth_token)

        client.messages.create(
            from_='+12073877090',
            to=phone_number,
            body=f"Your activation code is {code}"
        )

    thread = threading.Thread(target=send_in_thread)
    thread.start()

    return True