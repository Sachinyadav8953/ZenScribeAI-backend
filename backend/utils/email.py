from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from config import settings



mail_config = ConnectionConfig(
    MAIL_USERNAME   = settings.MAIL_USERNAME,
    MAIL_PASSWORD   = settings.MAIL_PASSWORD,  
    MAIL_FROM       = settings.MAIL_FROM,
    MAIL_FROM_NAME  = settings.MAIL_FROM_NAME,
    MAIL_PORT       = settings.MAIL_PORT,
    MAIL_SERVER     = settings.MAIL_SERVER,
    MAIL_STARTTLS   = settings.MAIL_STARTTLS,
    MAIL_SSL_TLS    = settings.MAIL_SSL_TLS,
    USE_CREDENTIALS = True,
)


fm = FastMail(mail_config)


async def send_reset_password_email(email: str, reset_token: str) -> None:

    reset_link = f"http://localhost:3000/reset-password?token={reset_token}"

    message = MessageSchema(
        subject     = "Doctor_zenZ — Reset Your Password",
        recipients  = [email],  
        body        = f"""
            <h2>Reset Your Password</h2>
            <p>You requested to reset your password.</p>
            <p>Click the link below — it expires in 15 minutes:</p>
            <a href="{reset_link}">Reset Password</a>
            <p>If you did not request this, ignore this email.</p>
        """,
        subtype     = MessageType.html      
    )

    await fm.send_message(message)          