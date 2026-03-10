import random
import string
from flask_mail import Mail, Message
from flask import current_app

mail = Mail()

def send_otp_email(email, otp):
    msg = Message('Verify your AgriAI Account',
                  sender=current_app.config['MAIL_USERNAME'],
                  recipients=[email])
    msg.body = f'Your OTP for registration is: {otp}. It will expire in 10 minutes.'
    try:
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def generate_otp():
    return ''.join(random.choices(string.digits, k=6))
