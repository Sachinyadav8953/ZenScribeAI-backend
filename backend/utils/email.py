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


async def send_verification_email(email: str, token: str) -> None:
    verify_link = f"http://localhost:3000/verify-email?token={token}"

    message = MessageSchema(
        subject    = "Doctor_zenZ — Verify Your Email",
        recipients = [email],
        body       = f"""
            <h2>Welcome to Doctor_zenZ</h2>
            <p>Please verify your email address to activate your account.</p>
            <p>Click the link below — it expires in 24 hours:</p>
            <a href="{verify_link}" 
               style="background:#2563EB;color:white;padding:10px 20px;
                      text-decoration:none;border-radius:5px;">
               Verify Email
            </a>
            <p>If you did not register, ignore this email.</p>
        """,
        subtype    = MessageType.html
    )

    await fm.send_message(message)


async def send_reset_password_email(email: str, token: str) -> None:
    reset_link = f"http://localhost:3000/reset-password?token={token}"

    message = MessageSchema(
        subject    = "Doctor_zenZ — Reset Your Password",
        recipients = [email],
        body       = f"""
            <h2>Reset Your Password</h2>
            <p>You requested to reset your password.</p>
            <p>Click the link below — it expires in 15 minutes:</p>
            <a href="{reset_link}"
               style="background:#2563EB;color:white;padding:10px 20px;
                      text-decoration:none;border-radius:5px;">
               Reset Password
            </a>
            <p>If you did not request this, ignore this email.</p>
        """,
        subtype    = MessageType.html
    )

    await fm.send_message(message)