import os
import requests
from config import Config

def send_verification_email(email, code):
    """
    Sends a verification code to the user's email using Brevo API.
    """
    subject = "Verify your Rank YourSelf Account"
    body = f"Your verification code is: {code}\n\nThis code will expire in 10 minutes."
    
    _send_mail_brevo(email, subject, body)

def send_reset_password_email(email, code):
    """
    Sends a password reset code to the user's email using Brevo API.
    """
    subject = "Reset your Rank YourSelf Password"
    body = f"Your password reset code is: {code}\n\nThis code will expire in 10 minutes."
    
    _send_mail_brevo(email, subject, body)

def _send_mail_brevo(to_email, subject, body):
    from dotenv import load_dotenv
    load_dotenv(override=True)

    api_key = os.environ.get('BREVO_API_KEY')
    # Use the email you registered with Brevo as the 'from' address
    from_email = os.environ.get('MAIL_FROM', 'rankyourself.01@gmail.com')

    if api_key:
        try:
            print(f"DEBUG: Attempting to send mail via Brevo API to {to_email}")
            url = "https://api.brevo.com/v3/smtp/email"
            headers = {
                "api-key": api_key,
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            data = {
                "sender": {"name": "Rank YourSelf", "email": from_email},
                "to": [{"email": to_email}],
                "subject": subject,
                "textContent": body
            }
            response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code in [200, 201, 202]:
                print(f"SUCCESS: Email sent to {to_email} via Brevo")
                return True
            else:
                print(f"ERROR: Brevo API failed (Status {response.status_code}): {response.text}")
        except Exception as e:
            print(f"ERROR: Failed to connect to Brevo API: {e}")
    else:
        print("DEBUG: BREVO_API_KEY not configured, falling back to console.")

    # Fallback to console for development
    print("\n" + "="*50)
    print(f"DEVELOPMENT MODE: Email to {to_email}")
    print(f"Subject: {subject}")
    print(f"Body: {body}")
    print("="*50 + "\n")
    return False
