# apps/notifications/admin.py

from django.contrib import admin
from .models import Notification

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = (
        'recipient_email', 
        'notification_type', 
        'title', 
        'is_read', 
        'created_at'
    )
    list_filter = (
        'notification_type', 
        'is_read', 
        'created_at'
    )
    search_fields = (
        'title', 
        'message', 
        'recipient__email', 
        'recipient__first_name',
        'recipient__last_name'
    )
    readonly_fields = (
        'recipient', 
        'sender',
        'notification_type', 
        'title', 
        'message',
        'created_at',
        'related_url'
    )

    @admin.display(description='Recipient')
    def recipient_email(self, obj):
        return obj.recipient.email