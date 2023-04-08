import os
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema
from core.config import config

class Mailer:
    conf = ConnectionConfig(
        MAIL_USERNAME = config.MAIL_USERNAME,
        MAIL_PASSWORD = config.MAIL_PASSWORD,
        MAIL_FROM = config.MAIL_USERNAME,
        MAIL_PORT = config.MAIL_PORT,
        MAIL_SERVER = config.MAIL_SERVER,
        MAIL_FROM_NAME = "IRyS Team",
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=False,
        TEMPLATE_FOLDER=os.path.join(os.getcwd(), "assets", "templates")
    )

    @staticmethod
    async def send_registration_otp_email(email_to: str, body: dict):
        message = MessageSchema(
            subject="Your One-Time Passcode (OTP) from IRyS!",
            recipients=[email_to],
            template_body=body,
            subtype="html",
        )
        fm = FastMail(Mailer.conf)
        await fm.send_message(message, template_name="registration_otp_email.html")

    @staticmethod
    async def send_forgot_password_otp_email(email_to: str, body: dict):
        message = MessageSchema(
            subject="Your Password Reset OTP from IRyS!",
            recipients=[email_to],
            template_body=body,
            subtype="html",
        )
        fm = FastMail(Mailer.conf)
        await fm.send_message(message, template_name="forgot_password_otp_email.html")