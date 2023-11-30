from django.conf import settings
from twilio.rest import Client


# the message handler for sending messages to the user during registration
class MessageHandler:
    phone_number = None
    otp = None

    def __init__(self, phone_number, otp) -> None:
        self.phone_number = phone_number
        self.otp = otp

    def send_otp_via_message(self):
        client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
        message = client.messages.create(
            body=f"your otp is {self.otp}",
            from_=f"{settings.TWILIO_PHONE_NUMBER}",
            to=f"{settings.COUNTRY_CODE}{self.phone_number}",
        )
