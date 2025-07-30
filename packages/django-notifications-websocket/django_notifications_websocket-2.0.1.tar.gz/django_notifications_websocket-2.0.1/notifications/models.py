import uuid

from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.query import QuerySet
from django.db.models import Count, When, Case

from notifications.managers import SignalTriggeringManager
from notifications.choices import NotificationsStatus


User = get_user_model()

# Import notification settings from Django settings
NOTIFICATIONS_SETTINGS = getattr(settings, "NOTIFICATIONS", {})


class BaseModel(models.Model):
    """Base class for all other models."""

    # Unique identifier.
    uid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        db_index=True,
        unique=True,
        help_text="Unique identifier for this model instance.",
    )
    # Timestamp indicating when the instance was created.
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp indicating when the instance was created.",
    )
    # Timestamp indicating when the instance was last updated.
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp indicating when the instance was last updated.",
    )

    class Meta:
        abstract = True


class Notification(BaseModel):
    """Notification model to store user notifications."""

    # The user associated with this notification.
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        db_index=True,
        related_name="user_notification",
        help_text="The user to whom this notification belongs.",
    )
    # JSON field to store the notification data.
    notification = models.JSONField(help_text="Notification data in JSON format.")
    # Indicates whether the notification has been read or not.
    is_read = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Indicates whether the notification has been read or not.",
    )
    # Additional custom information related to the notification.
    custom_info = models.JSONField(
        null=True,
        blank=True,
        help_text="Additional custom information related to the notification.",
    )
    # The user who created this notification.
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        db_index=True,
        related_name="user_notification_created_by",
        help_text="The user who created this notification.",
    )
    # Status of the notification (e.g., active, archived, deleted).
    status = models.CharField(
        max_length=20,
        choices=NotificationsStatus.choices,
        db_index=True,
        default=NotificationsStatus.ACTIVE,
        help_text="Status of the notification.",
    )

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    # Custom manager for the Notification model.
    objects = SignalTriggeringManager()

    def __str__(self):
        """
        Return a string representation of the notification.

        Returns:
            str: String representation of the notification.
        """
        return f"{self.user} - {self.notification.get('message', '')} - {self.is_read}"

    def clean(self):
        """
        Perform this action before saving the model instance.
        """
        from notifications.utils.notifications import validate_notification

        super().clean()
        validate_notification(notification_data=self.notification, use_for_model=True)

    def get_active_notifications(self):
        """
        Retrieve active notifications.

        Returns:
            QuerySet: A queryset of active notifications.
        """
        return self.__class__.objects.filter(
            status=NotificationsStatus.ACTIVE
        ).order_by("-pk")

    def get_current_user_notifications(self, user):
        """
        Retrieve notifications for the current user if notifications are enabled.

        Returns:
            QuerySet: A queryset of notifications, total, read and unread notifications count belonging to the current user.

        Raises:
            ValueError: If notifications are not enabled for the current user.
        """

        if not user:
            raise ValueError("User is missing.")

        if NotificationSettings().is_user_enable_notification(user=user):
            # Select related fields if specified in settings
            settings_select_related_fields = NOTIFICATIONS_SETTINGS.get(
                "NOTIFICATION_USER_SELECT_RELATED_FIELDS"
            )
            if settings_select_related_fields:
                select_related_fields = []
                for field in settings_select_related_fields:
                    select_related_fields.append(f"user__{field}")
                    select_related_fields.append(f"created_by__{field}")
            else:
                select_related_fields = ["user", "created_by"]

            # Prefetch related fields if specified in settings
            prefetch_related_fields = NOTIFICATIONS_SETTINGS.get(
                "NOTIFICATION_USER_PREFETCH_RELATED_FIELDS", []
            )

            # Get the user's notifications
            user_notifications = (
                Notification()
                .get_active_notifications()
                .filter(user=user)
                .select_related(*select_related_fields)
                .prefetch_related(*prefetch_related_fields)
            )

            # Aggregate the counts
            notification_counts = user_notifications.aggregate(
                total_notifications=Count("id"),
                read_notifications=Count(Case(When(is_read=True, then=1))),
            )

            return {
                "notifications": user_notifications,
                "total_notifications": notification_counts["total_notifications"],
                "read_notifications": notification_counts["read_notifications"],
                "unread_notifications": notification_counts["total_notifications"]
                - notification_counts["read_notifications"],
            }

        else:
            raise ValueError("Notifications are not enabled for the current user.")

    def get_current_user_unread_notifications(self, user):
        """
        Retrieve unread notifications of current user.

        Returns:
            QuerySet: A queryset of unread notifications of current user.
        """
        return (
            Notification()
            .get_current_user_notifications(user=user)["notifications"]
            .filter(is_read=False)
        )

    def get_current_user_read_notifications(self, user):
        """
        Retrieve read notifications of current user.

        Returns:
            QuerySet: A queryset of read notifications of current user.
        """
        return (
            Notification()
            .get_current_user_notifications(user=user)["notifications"]
            .filter(is_read=True)
        )

    def create_notification_for_users(
        self, notification_data: dict, users: QuerySet, requested_user, **kwargs
    ):
        """Create notifications for multiple users efficiently."""
        from notifications.utils.notifications import validate_notification

        # Validate notification data
        validate_notification(notification_data=notification_data)

        # If users is a single user instance, convert it to a queryset
        if not isinstance(users, QuerySet):
            users = QuerySet(model=User).filter(id=users.id)

        # Create notification instances for each user
        notification_instance = [
            Notification(
                user=user,
                notification=notification_data,
                created_by=requested_user,
                **kwargs,
            )
            for user in users
        ]
        # Use bulk_create to insert all instances in a single query
        Notification.objects.bulk_create(notification_instance)

        return


class NotificationSettings(BaseModel):
    """Model to store user notification settings."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="notification_settings",
        verbose_name="User",
    )
    is_enable_notification = models.BooleanField(
        default=True, verbose_name="Enable Notifications"
    )

    class Meta:
        verbose_name = "Notification Setting"
        verbose_name_plural = "Notification Settings"

    def __str__(self):
        """
        Return a string representation of the notification settings

        Returns:
            str: String representation of the notification settings
        """
        return f"{self.user.username} - Notifications Enabled: {self.is_enable_notification}"

    def is_user_enable_notification(self, user):
        """Check if notifications are enabled for the user"""
        try:
            return self.__class__.objects.get(user=user).is_enable_notification
        except self.__class__.DoesNotExist:
            raise ValueError("Notification settings instance missing for this user")
