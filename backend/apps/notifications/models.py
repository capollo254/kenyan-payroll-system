# apps/notifications/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class Notification(models.Model):
    """
    Represents a system notification for a user.
    """
    # Choices for the notification type
    NOTIFICATION_TYPE_CHOICES = (
        ('payslip_published', _('New Payslip Published')),
        ('payroll_run_completed', _('Payroll Run Completed')),
        ('system_alert', _('System Alert')),
        ('account_change', _('Account Information Change')),
        ('deduction_update', _('Deduction Information Updated')),
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text=_("The user who will receive the notification.")
    )
    
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_("The user who initiated the notification (e.g., an administrator).")
    )

    notification_type = models.CharField(
        _("Notification Type"),
        max_length=50,
        choices=NOTIFICATION_TYPE_CHOICES,
        help_text=_("The category or type of the notification.")
    )

    title = models.CharField(
        _("Title"),
        max_length=255,
        default=_("New Notification")
    )
    
    message = models.TextField(
        _("Message"),
        help_text=_("The main content of the notification.")
    )

    created_at = models.DateTimeField(
        _("Created At"),
        auto_now_add=True
    )
    
    is_read = models.BooleanField(
        _("Is Read"),
        default=False
    )
    
    # Optional: A URL to link to the relevant object (e.g., the new payslip)
    related_url = models.URLField(
        _("Related URL"),
        max_length=255,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"[{self.get_notification_type_display()}] for {self.recipient.email} at {self.created_at.date()}"

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']