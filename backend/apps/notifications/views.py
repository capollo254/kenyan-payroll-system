# apps/notifications/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Notification
from .serializers import NotificationSerializer

class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A viewset for users to retrieve, mark as read, and delete their notifications.
    """
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Ensures a user can only view their own notifications.
        """
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')

    @action(detail=False, methods=['post'], url_path='mark-all-read')
    def mark_all_as_read(self, request, *args, **kwargs):
        """
        Marks all of the user's unread notifications as read.
        """
        unread_notifications = self.get_queryset().filter(is_read=False)
        count = unread_notifications.update(is_read=True)
        return Response({'message': f'{count} notifications marked as read.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='mark-as-read')
    def mark_as_read(self, request, pk=None):
        """
        Marks a single notification as read.
        """
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'message': 'Notification marked as read.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        """
        Returns the count of unread notifications for the user.
        """
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count}, status=status.HTTP_200_OK)