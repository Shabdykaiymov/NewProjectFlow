from django.db import models
from django.contrib.auth.models import User


class GoogleCalendarCredentials(models.Model):
    """
    Модель для хранения данных авторизации Google Calendar.

    Содержит токены и другую информацию для доступа к Google Calendar API.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='google_credentials')
    access_token = models.TextField(verbose_name="Токен доступа")
    refresh_token = models.TextField(verbose_name="Токен обновления")
    token_expiry = models.DateTimeField(verbose_name="Срок действия токена")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Учетные данные Google Calendar"
        verbose_name_plural = "Учетные данные Google Calendar"

    def __str__(self):
        return f"Google Calendar данные для {self.user.username}"