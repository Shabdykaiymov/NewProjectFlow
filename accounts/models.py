from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models.signals import post_migrate


class UserProfile(models.Model):
    """
    Расширение стандартной модели пользователя Django.

    Хранит дополнительную информацию о пользователе, такую как
    настройки оповещений и другие персональные данные.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    email_notifications = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Профиль {self.user.username}"


# Сигнал для автоматического создания профиля при создании пользователя
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_migrate)
def create_profiles_for_existing_users(sender, **kwargs):
    if sender.name == 'accounts':
        for user in User.objects.all():
            UserProfile.objects.get_or_create(user=user)