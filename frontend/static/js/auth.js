/**
 * Модуль для работы с аутентификацией
 */

// Базовый URL API
const API_URL = '/api';


/**
 * Обновляет информацию о текущем пользователе в интерфейсе
 */
async function updateUserInfo() {
    try {
        // Проверяем, авторизован ли пользователь
        if (!localStorage.getItem('access_token')) {
            return;
        }

        // Выполняем запрос к API для получения информации о пользователе
        const response = await fetch(`${API_URL}/auth/me/`, {
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('access_token')}`
            }
        });

        if (!response.ok) {
            throw new Error('Не удалось получить информацию о пользователе');
        }

        const userData = await response.json();

        // Обновляем отображаемое имя пользователя
        const usernameElement = document.getElementById('currentUsername');
        if (usernameElement) {
            if (userData.first_name || userData.last_name) {
                usernameElement.textContent = `${userData.first_name || ''} ${userData.last_name || ''}`.trim();
            } else {
                usernameElement.textContent = userData.username;
            }
        }
    } catch (error) {
        console.error('Ошибка при получении информации о пользователе:', error);
    }
}
/**
 * Выполняет выход пользователя из системы
 */
async function logout() {
    try {
        const refreshToken = localStorage.getItem('refresh_token');

        if (refreshToken) {
            try {
                await fetch(`${API_URL}/auth/logout/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
                    },
                    body: JSON.stringify({ refresh: refreshToken }),
                });
            } catch (e) {
                console.error('Ошибка при отправке запроса на выход:', e);
            }
        }

        // Очищаем локальное хранилище
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_key');

        // Перенаправляем на страницу входа
        window.location.href = '/login/';
        return false;
    } catch (error) {
        console.error('Ошибка при выходе:', error);
        // В любом случае очищаем хранилище и перенаправляем
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user_key');
        window.location.href = '/login/';
        return false;
    }
}
// Добавляем обработчик для кнопки выхода
document.addEventListener('DOMContentLoaded', function() {

    if (localStorage.getItem('access_token')) {
        // Обновляем информацию о пользователе
        updateUserInfo();
    } else if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/register')) {
        // Если пользователь не авторизован и не на странице входа или регистрации,
        // перенаправляем на страницу входа
        window.location.href = '/login/';

    const logoutLink = document.querySelector('a[href="/logout/"]');
    if (logoutLink) {
        logoutLink.addEventListener('click', function(e) {
            e.preventDefault();
            logout();
        });
    }
});