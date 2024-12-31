from django.http import HttpResponse
from django.core.mail import send_mail


def send_email(request):

    send_mail(subject='thats your subject',
                message='this is your message body', 
                from_email='tanzila@nccsuetp.com',
                recipients=['engr.tanzila786@gmail.com'])
    return HttpResponse(request,"Kamal")

