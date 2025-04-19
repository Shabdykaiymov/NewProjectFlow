from django.urls import path
from .views import GoogleAuthUrlView, GoogleAuthCallbackView, SyncTaskWithCalendarView, GoogleCalendarStatusView

urlpatterns = [
    path('auth-url/', GoogleAuthUrlView.as_view(), name='google-auth-url'),
    path('callback/', GoogleAuthCallbackView.as_view(), name='google-auth-callback'),
    path('sync-task/<int:task_id>/', SyncTaskWithCalendarView.as_view(), name='sync-task-with-calendar'),
    path('status/', GoogleCalendarStatusView.as_view(), name='google-calendar-status'),
]