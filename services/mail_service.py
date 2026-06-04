import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

def send_verification_email(email, code):
    """
    Sends a verification code to the user's email using SMTP.
    """
    subject = "Verify your Rank YourSelf Account"
    body = f"Your verification code is: {code}\n\nThis code will expire in 10 minutes."
    
    _send_mail_smtp(email, subject, body)

def send_reset_password_email(email, code):
    """
    Sends a password reset code to the user's email using SMTP.
    """
    subject = "Reset your Rank YourSelf Password"
    body = f"Your password reset code is: {code}\n\nThis code will expire in 10 minutes."
    
    _send_mail_smtp(email, subject, body)

def _send_mail_smtp(to_email, subject, body):
    # Ensure environment variables are re-loaded from .env file
    from dotenv import load_dotenv
    load_dotenv(override=True)

    # Check if SMTP is configured
    smtp_server = os.environ.get('MAIL_SERVER')
    smtp_port = os.environ.get('MAIL_PORT')
    smtp_user = os.environ.get('MAIL_USERNAME')
    smtp_pass = os.environ.get('MAIL_PASSWORD')

    print(f"DEBUG: Attempting to send mail via SMTP. Server: {smtp_server}, Port: {smtp_port}, User: {smtp_user}")

    if all([smtp_server, smtp_port, smtp_user, smtp_pass]):
        try:
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            print("DEBUG: Connecting to SMTP server...")
            server = smtplib.SMTP(smtp_server, int(smtp_port))
            server.set_debuglevel(1) # Enable verbose SMTP logging
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
            server.quit()
            print(f"SUCCESS: Email sent to {to_email}")
            return True
        except Exception as e:
            print(f"ERROR: Failed to send email via SMTP: {e}")
    else:
        print("DEBUG: SMTP not fully configured, falling back to console.")
    
    # Fallback to console for development
    print("\n" + "="*50)
    print(f"DEVELOPMENT MODE: Email to {to_email}")
    print(f"Subject: {subject}")
    print(f"Body: {body}")
    print("="*50 + "\n")
    return False
