from django.urls import path
from .views import TasksByStatusView, TasksCompletionView, TasksDeadlineView, TasksByAssigneeView

urlpatterns = [
    path('project/<int:project_id>/tasks-by-status/', TasksByStatusView.as_view(), name='tasks-by-status'),
    path('project/<int:project_id>/tasks-completion/', TasksCompletionView.as_view(), name='tasks-completion'),
    path('project/<int:project_id>/tasks-deadline/', TasksDeadlineView.as_view(), name='tasks-deadline'),
    path('project/<int:project_id>/tasks-by-assignee/', TasksByAssigneeView.as_view(), name='tasks-by-assignee'),
]