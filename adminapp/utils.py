
from notification.utils import create_notification

def overallnotification(sender_id, receiver_id, event, subject, message, notification_message, iu_id, request_user):
    data = {
        'sender': sender_id,
        'receiver': receiver_id,
        'event': event,
        'subject': subject,
        'message': message,
        'notification_message': notification_message,
        'redirect_link': "https://example.com/",
        'iu_id': iu_id
    }
    notification_response = create_notification(data, request_user)
    return notification_response
