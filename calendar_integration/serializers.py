from rest_framework import serializers
from .models import GoogleCalendarCredentials

class GoogleCalendarCredentialsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для учетных данных Google Calendar.
    Используется для сохранения и обновления токенов Google OAuth2.
    """
    class Meta:
        model = GoogleCalendarCredentials
        fields = ('access_token', 'refresh_token', 'token_expiry')
        extra_kwargs = {
            'access_token': {'write_only': True},
            'refresh_token': {'write_only': True}
        }