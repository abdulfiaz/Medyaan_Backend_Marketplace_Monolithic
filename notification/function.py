from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import NotificationSerializer
from .models import *
from adminapp.iudetail import *
from users.auth import *
from users.models import *
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from .serializers import NotificationSerializer
from .models import Notification, EventMaster, TemplateMaster
from .models import get_email


def create_notification(data, request_user):
    
    iu_id = data.get('iu_id')
    if not iu_id:
        return {'status': 'error', 'message': 'IU domain not found.', 'status_code': status.HTTP_404_NOT_FOUND}
    if not data:
        return {'status': 'error', 'message': 'No data received.'}

    receiver_id = data.get('receiver')
    if receiver_id:
        receiver_email = get_email(receiver_id)
        if receiver_email:
            data['email_id'] = receiver_email
        else:
            return {'status': 'error', 'message': 'Receiver email not found.', 'status_code': status.HTTP_404_NOT_FOUND}
    else:
        return {'status': 'error', 'message': 'Receiver ID not provided.', 'status_code': status.HTTP_400_BAD_REQUEST}
 
    event_id = data.get('event')
    if event_id:
        try:
            event = EventMaster.objects.get(id=event_id)
            data['role'] = event.role
            # template = TemplateMaster.objects.get(id=event.sms_templateid)
            # formatted_message = template.content.format(data.get('notification_message', ''))
            # data['notification_message'] = formatted_message
        except EventMaster.DoesNotExist:
            return {'status': 'error', 'message': 'Event or Template not found.', 'status_code': status.HTTP_404_NOT_FOUND}
    else:
        return {'status': 'error', 'message': 'Event ID not provided.', 'status_code': status.HTTP_400_BAD_REQUEST}
    
    notification_data = {
    'sender': data.get('sender'),
    'receiver': receiver_id,
    'event': event_id,
    'subject': data.get('subject', ''),
    'message': data.get('message', ''),
    'notification_message':data.get('notification_message'),
    'redirect_link': data.get('redirect_link', "https://example.com/"),
    'role': data['role'],
    'email_id':data['email_id'],
    'iu_id': iu_id
    }
    try:
        serializer = NotificationSerializer(data=notification_data)
        if serializer.is_valid():
            notification = serializer.save(created_by=request_user)
            return {'status': 'success', 'message': 'Notification created successfully.', 'data': notification.id, 'status_code': status.HTTP_201_CREATED}
        else:
            return {'status': 'error', 'message': 'Notification not created.', 'data': serializer.errors, 'status_code': status.HTTP_400_BAD_REQUEST}
    except Exception as e:
        return {'status': 'error', 'message': 'Unexpected error occurred.'}
