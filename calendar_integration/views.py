from rest_framework import views, permissions, status
from rest_framework.response import Response
from django.conf import settings
from django.shortcuts import redirect
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from .models import GoogleCalendarCredentials
from tasks.models import Task
import datetime


class GoogleAuthUrlView(views.APIView):
    """
    API эндпоинт для получения URL авторизации Google OAuth2.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        # Создаем flow для OAuth2 авторизации
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            },
            scopes=["https://www.googleapis.com/auth/calendar"]
        )

        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

        # Генерируем URL авторизации
        authorization_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent"  # Всегда запрашиваем refresh_token
        )

        # Сохраняем state в сессии для проверки при callback
        request.session["google_auth_state"] = state

        return Response({"authorization_url": authorization_url})


class GoogleAuthCallbackView(views.APIView):
    """
    API эндпоинт для обработки callback от Google OAuth2.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        # Получаем state и код из параметров запроса
        state = request.GET.get("state")
        code = request.GET.get("code")

        # Проверяем state из сессии
        session_state = request.session.get("google_auth_state")
        if state != session_state:
            return Response(
                {"detail": "Invalid state parameter."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Создаем flow для обмена кода на токены
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uris": [settings.GOOGLE_REDIRECT_URI],
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token"
                }
            },
            scopes=["https://www.googleapis.com/auth/calendar"]
        )

        flow.redirect_uri = settings.GOOGLE_REDIRECT_URI

        # Обмениваем код на токены
        flow.fetch_token(code=code)

        # Получаем учетные данные
        credentials = flow.credentials

        # Сохраняем учетные данные в базе данных
        GoogleCalendarCredentials.objects.update_or_create(
            user=request.user,
            defaults={
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_expiry": datetime.datetime.fromtimestamp(credentials.expiry.timestamp())
            }
        )

        # Редирект на фронтенд
        return redirect("/calendar-settings?success=true")


class SyncTaskWithCalendarView(views.APIView):
    """
    API эндпоинт для синхронизации задачи с Google Calendar.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, task_id):
        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            return Response(
                {"detail": "Задача не найдена."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Проверяем, является ли пользователь участником проекта
        if not task.project.members.filter(id=request.user.id).exists():
            return Response(
                {"detail": "У вас нет доступа к этой задаче."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Проверяем, есть ли у пользователя учетные данные Google Calendar
        try:
            google_credentials = GoogleCalendarCredentials.objects.get(user=request.user)
        except GoogleCalendarCredentials.DoesNotExist:
            return Response(
                {"detail": "Необходимо сначала авторизоваться в Google Calendar."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Создаем учетные данные для API
        credentials = Credentials(
            token=google_credentials.access_token,
            refresh_token=google_credentials.refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET,
            scopes=["https://www.googleapis.com/auth/calendar"]
        )

        # Создаем сервис календаря
        calendar_service = build("calendar", "v3", credentials=credentials)

        # Определяем параметры события
        event = {
            "summary": task.title,
            "description": task.description or "",
            "start": {
                "dateTime": task.due_date.isoformat() if task.due_date else datetime.datetime.now().isoformat(),
                "timeZone": "Europe/Moscow"
            },
            "end": {
                "dateTime": (task.due_date + datetime.timedelta(hours=1)).isoformat() if task.due_date else (
                            datetime.datetime.now() + datetime.timedelta(hours=1)).isoformat(),
                "timeZone": "Europe/Moscow"
            }
        }

        # Проверяем, есть ли уже событие в календаре
        if task.google_calendar_event_id:
            # Обновляем существующее событие
            updated_event = calendar_service.events().update(
                calendarId="primary",
                eventId=task.google_calendar_event_id,
                body=event
            ).execute()
        else:
            # Создаем новое событие
            created_event = calendar_service.events().insert(
                calendarId="primary",
                body=event
            ).execute()

            # Сохраняем ID события в задаче
            task.google_calendar_event_id = created_event["id"]
            task.save()

        return Response({"detail": "Задача успешно синхронизирована с Google Calendar."})


class GoogleCalendarStatusView(views.APIView):
    """
    API эндпоинт для проверки статуса авторизации Google Calendar.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        # Проверяем, есть ли у пользователя учетные данные Google Calendar
        has_credentials = GoogleCalendarCredentials.objects.filter(user=request.user).exists()

        return Response({
            "authorized": has_credentials
        })