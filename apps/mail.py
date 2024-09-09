from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse


def send_email(_subject, _msg, _recipient):
    from_email = settings.EMAIL_HOST_USER
    try:
        send_mail(_subject, _msg, from_email, _recipient)
    except Exception:
        pass

    return HttpResponse('Email sent')
