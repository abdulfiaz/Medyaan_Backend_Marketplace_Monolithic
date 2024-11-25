
from rest_framework import status
from notification.serializers import NotificationSerializer

def overallnotification(sender_id, receiver_id, event, subject, message, notification_message, iu_id, request_user,role,email_id,email_content=None):
    data = {
        'sender': sender_id,
        'receiver': receiver_id,
        'event': event,
        'subject': subject,
        'message': message,
        'notification_message': notification_message,
        'redirect_link': "https://example.com/",
        'iu_id': iu_id,
        'email_content': email_content,
        'role':role,
        'email_id':email_id
    }
    try:
        serializer = NotificationSerializer(data=data)
        if serializer.is_valid():
            notification = serializer.save(created_by=request_user)
    except Exception as e:
        return {'status': 'error', 'message': 'Unexpected error occurred.'}

