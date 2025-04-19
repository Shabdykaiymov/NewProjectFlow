from rest_framework import views, permissions, status
from rest_framework.response import Response
from django.db.models import Count, F, Q
from django.utils import timezone
from datetime import timedelta
from projects.models import Project
from tasks.models import Task, TaskStatus


class TasksByStatusView(views.APIView):
    """
    API эндпоинт для получения статистики задач по статусам.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id, members=request.user)
        except Project.DoesNotExist:
            return Response(
                {"detail": "Проект не найден или у вас нет к нему доступа."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Получаем количество задач по статусам
        statuses = TaskStatus.objects.filter(project=project).annotate(
            tasks_count=Count('tasks')
        ).values('id', 'name', 'tasks_count')

        return Response(statuses)


class TasksCompletionView(views.APIView):
    """
    API эндпоинт для получения статистики выполнения задач.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id, members=request.user)
        except Project.DoesNotExist:
            return Response(
                {"detail": "Проект не найден или у вас нет к нему доступа."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Определяем завершенные и незавершенные статусы
        # Предполагаем, что статус "Завершена" имеет в названии слово "завершена" или "готово"
        completed_statuses = TaskStatus.objects.filter(
            project=project
        ).filter(
            name__icontains='заверш'
        ).values_list('id', flat=True)

        # Считаем завершенные и незавершенные задачи
        completed_tasks_count = Task.objects.filter(
            project=project,
            status_id__in=completed_statuses
        ).count()

        total_tasks_count = Task.objects.filter(project=project).count()
        incomplete_tasks_count = total_tasks_count - completed_tasks_count

        # Формируем данные для диаграммы
        completion_data = {
            'completed': completed_tasks_count,
            'incomplete': incomplete_tasks_count,
            'total': total_tasks_count,
            'completion_rate': round(completed_tasks_count / total_tasks_count * 100, 2) if total_tasks_count > 0 else 0
        }

        return Response(completion_data)


class TasksDeadlineView(views.APIView):
    """
    API эндпоинт для получения статистики по дедлайнам задач.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id, members=request.user)
        except Project.DoesNotExist:
            return Response(
                {"detail": "Проект не найден или у вас нет к нему доступа."},
                status=status.HTTP_404_NOT_FOUND
            )

        now = timezone.now()

        # Подсчет просроченных задач (дедлайн прошел, но задача не завершена)
        completed_statuses = TaskStatus.objects.filter(
            project=project, name__icontains='заверш'
        ).values_list('id', flat=True)

        overdue_tasks_count = Task.objects.filter(
            project=project,
            due_date__lt=now,
            status_id__in=completed_statuses
        ).count()

        # Подсчет задач, которые нужно выполнить скоро (в течение 3 дней)
        upcoming_tasks_count = Task.objects.filter(
            project=project,
            due_date__gt=now,
            due_date__lt=now + timedelta(days=3)
        ).exclude(
            status_id__in=completed_statuses
        ).count()

        # Подсчет задач без дедлайна
        no_deadline_tasks_count = Task.objects.filter(
            project=project,
            due_date__isnull=True
        ).count()

        deadline_data = {
            'overdue': overdue_tasks_count,
            'upcoming': upcoming_tasks_count,
            'no_deadline': no_deadline_tasks_count
        }

        return Response(deadline_data)


class TasksByAssigneeView(views.APIView):
    """
    API эндпоинт для получения статистики задач по исполнителям.
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, project_id):
        try:
            project = Project.objects.get(id=project_id, members=request.user)
        except Project.DoesNotExist:
            return Response(
                {"detail": "Проект не найден или у вас нет к нему доступа."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Получаем количество задач по исполнителям
        tasks_by_assignee = Task.objects.filter(
            project=project
        ).values(
            'assignee__username'
        ).annotate(
            tasks_count=Count('id')
        )

        # Преобразуем результат в более удобный формат
        result = []
        for item in tasks_by_assignee:
            username = item['assignee__username'] or 'Не назначено'
            result.append({
                'assignee': username,
                'tasks_count': item['tasks_count']
            })

        return Response(result)