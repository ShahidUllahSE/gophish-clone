from django.core.mail import send_mail
from django.conf import settings
def send_mail_to_client():
    subject ="This email is from django"
    message = "This is test meassage from django"
    from_email = settings.EMAIL_HOST_USER
    recipient_list = ['simulationtools5@gmail.com']
    send_mail(subject, message, from_email,recipient_list)