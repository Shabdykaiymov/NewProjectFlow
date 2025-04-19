from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def index_view(request):
    """Главная страница - перенаправляет на список проектов для авторизованных
       или на страницу входа для неавторизованных"""
    if request.user.is_authenticated:
        return redirect('project_list')
    else:
        return redirect('login')

def login_view(request):
    """Страница входа"""
    # Если пользователь авторизован и пытается войти через URL,
    # мы не перенаправляем его, чтобы он мог выйти
    return render(request, 'accounts/login.html')

def register_view(request):
    """Страница регистрации"""
    # Аналогично, не перенаправляем авторизованного пользователя
    return render(request, 'accounts/register.html')

@login_required
def project_list_view(request):
    """Страница со списком проектов"""
    return render(request, 'projects/list.html')

@login_required
def project_detail_view(request, project_id):
    """Страница проекта с канбан-доской"""
    return render(request, 'projects/detail.html', {'project_id': project_id})

@login_required
def analytics_view(request):
    """Страница аналитики"""
    return render(request, 'analytics/index.html')

def logout_view(request):
    """
    Страница выхода из системы
    """
    from django.contrib.auth import logout
    logout(request)
    return redirect('login')

def test_view(request):
    """Тестовая страница для отладки"""
    return render(request, 'test.html')