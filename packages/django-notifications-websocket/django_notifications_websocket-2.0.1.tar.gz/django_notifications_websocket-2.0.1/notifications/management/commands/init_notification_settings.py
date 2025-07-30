from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from notifications.models import NotificationSettings


User = get_user_model()


class Command(BaseCommand):
    help = "Initialize Notification Settings for Users"

    def handle(self, *args, **options):
        users_notification_settings = []

        self.stdout.write(self.style.SUCCESS("Initializing Notification Settings..."))

        # Arrange to create NotificationSettings for each user
        for user in User.objects.all():
            users_notification_settings.append(
                NotificationSettings(
                    user=user,
                )
            )

        # Bulk create NotificationSettings for all users
        NotificationSettings.objects.bulk_create(
            users_notification_settings, batch_size=300, ignore_conflicts=True
        )

        self.stdout.write(
            self.style.SUCCESS(f"Notification Settings Initialized For All Users...")
        )
