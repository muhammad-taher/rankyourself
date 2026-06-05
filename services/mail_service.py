import os
import requests
from config import Config

def send_verification_email(email, code):
    """
    Sends a verification code to the user's email using Resend API.
    """
    subject = "Verify your Rank YourSelf Account"
    body = f"Your verification code is: {code}\n\nThis code will expire in 10 minutes."
    
    _send_mail_resend(email, subject, body)

def send_reset_password_email(email, code):
    """
    Sends a password reset code to the user's email using Resend API.
    """
    subject = "Reset your Rank YourSelf Password"
    body = f"Your password reset code is: {code}\n\nThis code will expire in 10 minutes."
    
    _send_mail_resend(email, subject, body)

def _send_mail_resend(to_email, subject, body):
    from dotenv import load_dotenv
    load_dotenv(override=True)

    api_key = os.environ.get('RESEND_API_KEY')
    # Default 'from' address for Resend free tier if domain is not verified
    from_email = os.environ.get('MAIL_FROM', 'onboarding@resend.dev')

    if api_key:
        try:
            print(f"DEBUG: Attempting to send mail via Resend API to {to_email}")
            url = "https://api.resend.com/emails"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "from": f"Rank YourSelf <{from_email}>",
                "to": [to_email],
                "subject": subject,
                "text": body
            }
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code in [200, 201]:
                print(f"SUCCESS: Email sent to {to_email} via Resend")
                return True
            else:
                print(f"ERROR: Resend API failed (Status {response.status_code}): {response.text}")
        except Exception as e:
            print(f"ERROR: Failed to connect to Resend API: {e}")
    else:
        print("DEBUG: RESEND_API_KEY not configured, falling back to console.")

    # Fallback to console for development
    print("\n" + "="*50)
    print(f"DEVELOPMENT MODE: Email to {to_email}")
    print(f"Subject: {subject}")
    print(f"Body: {body}")
    print("="*50 + "\n")
    return False
