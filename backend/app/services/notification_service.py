from app.core.config import settings


def send_sms(phone_number: str, message: str) -> bool:
    if settings.SMS_PROVIDER == "mock":
        print(f"[SMS] To: {phone_number} | {message}")
        return True

    if settings.SMS_PROVIDER == "twilio":
        try:
            from twilio.rest import Client
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=message,
                from_=settings.TWILIO_FROM_NUMBER,
                to=phone_number,
            )
            return True
        except Exception as exc:
            print(f"[SMS ERROR] {phone_number}: {exc}")
            return False

    raise ValueError(f"Unknown SMS_PROVIDER: {settings.SMS_PROVIDER}")