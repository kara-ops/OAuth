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


def forgot_pass(code:int,link:str):
    resend.api_key = settings.RESEND_API_KEY

    params = {
        "from": settings.RESEND_FROM_EMAIL,
        "to": ["raneankush93@gmail.com"],
        "subject": "Forgot password verification",
        "html": f"<p>Hello Ankush 👋<br>You have recieved your code:{code} .</p>"
    }
    email: resend.Emails.SendResponse = resend.Emails.send(params)
