from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr, BaseModel
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()


class EmailSchema(BaseModel):
    email: List[EmailStr]
    subject: str
    body: str


try:
    conf = ConnectionConfig(
        MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
        MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
        MAIL_FROM=os.getenv("MAIL_FROM"),
        MAIL_PORT=int(os.getenv("MAIL_PORT", 587)),
        MAIL_SERVER=os.getenv("MAIL_SERVER"),
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
    )

    # Create FastMail instance
    mail = FastMail(conf)
    print(
        f"Email configuration initialized successfully for {os.getenv('MAIL_USERNAME')}"
    )

except Exception as e:
    print(f"Failed to initialize email configuration: {str(e)}")
    raise


def create_otp_email_template(first_name: str, otp: str) -> str:
    """Create HTML email template for OTP"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .container {{ max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif; }}
            .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .otp-code {{ background-color: #e7f3ff; padding: 15px; text-align: center; font-size: 24px; font-weight: bold; border-radius: 5px; margin: 20px 0; }}
            .footer {{ padding: 20px; text-align: center; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Vibeprep - Email Verification</h1>
            </div>
            <div class="content">
                <h2>Hello {first_name}!</h2>
                <p>Thank you for signing up with Vibeprep. To complete your registration, please use the following OTP:</p>
                <div class="otp-code">{otp}</div>
                <p>This OTP will expire in 10 minutes.</p>
                <p>If you didn't request this verification, please ignore this email.</p>
            </div>
            <div class="footer">
                <p>© 2024 Vibeprep. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """


async def send_email(email: EmailSchema):
    """
    Send email using FastMail
    """
    try:
        message = MessageSchema(
            subject=email.subject,
            recipients=email.email,
            body=email.body,
            subtype=MessageType.html,
        )

        await mail.send_message(message)
        print(f"Email sent successfully to {email.email}")
        return {"message": "Email has been sent"}
    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        raise Exception(f"Failed to send email: {str(e)}")


async def send_otp_email(email: str, otp: str, first_name: str):
    """
    Send OTP verification email
    """
    try:
        print(f"Attempting to send OTP email to {email}")
        email_body = create_otp_email_template(first_name, otp)
        email_data = EmailSchema(
            email=[email], subject="Vibeprep - Email Verification Code", body=email_body
        )

        result = await send_email(email_data)
        return result
    except Exception as e:
        print(f"Failed to send OTP email to {email}: {str(e)}")
        raise Exception(f"Failed to send OTP email: {str(e)}")
