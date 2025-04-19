from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для профиля пользователя.
    Используется для получения/обновления дополнительной информации о пользователе.
    """

    class Meta:
        model = UserProfile
        fields = ('email_notifications',)


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для пользователя.
    Используется для отображения информации о пользователе в API.
    """
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'profile')
        read_only_fields = ('id',)


class RegisterSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации новых пользователей.
    Проверяет валидность пароля и создает нового пользователя.
    """
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')

    def validate(self, attrs):
        # Проверяем, что пароли совпадают
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Пароли не совпадают."})
        return attrs

    def create(self, validated_data):
        # Удаляем поле password2, так как оно не нужно для создания пользователя
        validated_data.pop('password2')

        # Создаем пользователя
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', '')
        )

        # Устанавливаем пароль
        user.set_password(validated_data['password'])
        user.save()

        return user