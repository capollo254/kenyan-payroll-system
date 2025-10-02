# apps/notifications/tasks.py

from celery import shared_task
from django.conf import settings
from .models import Notification

@shared_task
def create_notification_task(recipient_id, notification_type, title, message, related_url=None):
    """
    An asynchronous task to create a new notification.
    
    Args:
        recipient_id (int): The ID of the User to receive the notification.
        notification_type (str): The type of notification (e.g., 'payslip_published').
        title (str): The title of the notification.
        message (str): The body of the notification.
        related_url (str, optional): A URL to link to the related object.
    """
    try:
        User = settings.AUTH_USER_MODEL
        recipient = User.objects.get(id=recipient_id)
        
        Notification.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            related_url=related_url
        )
        
    except Exception as e:
        # Log the error for debugging
        print(f"Failed to create notification for user {recipient_id}: {e}")