from app.core.config import settings

import resend

resend.api_key = settings.RESEND_API_KEY

params = {
    "from": settings.RESEND_FROM_EMAIL,
    "to": ["raneankush93@gmail.com"],
    "subject": "gay",
    "html": "<p>Hello Ankush 👋<br>This is a test email sent using Resend free tier.</p>"
}

email: resend.Emails.SendResponse = resend.Emails.send(params)
print(email)