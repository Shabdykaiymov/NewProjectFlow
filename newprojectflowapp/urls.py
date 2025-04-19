"""
URL configuration for newprojectflowapp project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from frontend import views as frontend_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # API эндпоинты
    path('api/auth/', include('accounts.urls')),
    path('api/projects/', include('projects.urls')),
    path('api/tasks/', include('tasks.urls')),
    path('api/calendar/', include('calendar_integration.urls')),
    path('api/analytics/', include('analytics.urls')),

    # Добавляем URL-схемы для браузерного API
    path('api-auth/', include('rest_framework.urls')),

    # Frontend URLs
    path('', frontend_views.index_view, name='index'),
    path('login/', frontend_views.login_view, name='login'),
    path('register/', frontend_views.register_view, name='register'),
    path('projects/', frontend_views.project_list_view, name='project_list'),
    path('projects/<int:project_id>/', frontend_views.project_detail_view, name='project_detail'),
    path('analytics/', frontend_views.analytics_view, name='analytics'),
    path('logout/', frontend_views.logout_view, name='logout'),
    path('test/', frontend_views.test_view, name='test')
]

# Добавляем статические файлы в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
