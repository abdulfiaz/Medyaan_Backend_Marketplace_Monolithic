import re
from django.db import models
from requests import Response
from adminapp.models import BaseModel, IUMaster
from django.core.mail import EmailMessage
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from users.models import *
from rest_framework import status

from django.template.loader import render_to_string
class TemplateMaster(BaseModel):
    template_name = models.CharField(max_length=100, blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    class Meta:
        db_table = 'template_master'
        ordering = ['created_at']

class EventMaster(BaseModel):
    name = models.CharField(max_length=100, null=True, blank=True)
    email = models.BooleanField(default=False)
    role = models.CharField(max_length=50, null=True, blank=True)
    sms_templateid = models.CharField(max_length=50,blank=True,null=True)
    iu_id = models.ForeignKey(IUMaster, related_name='Eventmaster_iu_id', on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'event_master'
        ordering = ['created_at']

class Notification(BaseModel):
    event = models.ForeignKey(EventMaster,related_name='event_id', on_delete=models.DO_NOTHING)
    sender = models.CharField(max_length=200, blank=True, null=True)
    receiver = models.CharField(max_length=200, blank=True, null=True)
    subject = models.CharField(max_length=100,blank=True, null=True)
    message=models.TextField(blank=True,null=True)
    email_id = models.CharField(max_length=100,null=True,blank=True)
    notification_message = models.TextField(blank=True, null=True)
    redirect_link = models.CharField(max_length=100,blank=True, null=True) 
    role = models.CharField(max_length=100, null=True, blank=True)
    iu_id = models.ForeignKey(IUMaster, related_name='Notification_iu_id', on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'notification'
        ordering = ['created_at']

def get_email(user_id):
    try:
        user =CustomUser.objects.get(id=user_id)
        return user.email
    except CustomUser.DoesNotExist:
        return None

import logging

@receiver(post_save, sender=Notification)
def send_notification_in_email(sender, instance, created, **kwargs):
    if instance.event.email:
        sender_id = instance.sender
        receiver_id = instance.receiver

        sender_email = get_email(sender_id)
        receiver_email = get_email(receiver_id)

        if not sender_email or not receiver_email:
            return None
        match = re.search(r"Application ID:\s*(\d+)", instance.notification_message)
        application_id = match.group(1) if match else "N/A"
        context = {
            'subject': instance.subject,
            'message': instance.message,
            'application_id': application_id,
            'details': instance.notification_message,
        }
    
        try:
            email_content = render_to_string('email/notification_email.html', context)
            logging.info("Email content rendered successfully.")
        except Exception as e:
            logging.error(f"Failed to render email content: {e}")
            return

        subject = instance.subject
        email = EmailMessage(
            subject=subject,
            body=email_content,
            from_email=sender_email,
            to=[receiver_email]
        )
        email.content_subtype = "html"
        email.send(fail_silently=False)


