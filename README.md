# Система компьютерного тестирования — Backend

Серверная часть системы тестирования на Django + Django REST Framework. Предоставляет REST API для WPF-клиента и веб-интерфейс для преподавателей.

## Возможности

### Веб-интерфейс (преподаватель)
- Регистрация и авторизация (роли: студент, преподаватель, администратор)
- Создание, редактирование, удаление тестов
- Управление вопросами трёх типов: один правильный ответ, несколько правильных, открытый вопрос
- Настройки теста: время, количество попыток, перемешивание вопросов и ответов, случайная выборка N вопросов из банка
- Публикация/скрытие тестов
- Просмотр результатов с фильтрами (по тесту, по студенту)
- Ручная проверка открытых вопросов
- Статистика сложности вопросов (% правильных ответов)
- Экспорт результатов в Excel (.xlsx)
- Тёмная и светлая тема

### REST API (для WPF-клиента)
- Регистрация / авторизация по JWT-токенам
- Получение списка опубликованных тестов
- Старт теста (с проверкой попыток и случайной выборкой вопросов)
- Отправка ответов и автоматическая проверка
- Получение списка результатов
- Подробный разбор результата (что выбрал, где ошибся)
- Поддержка отслеживания переключения окон (античит)

## Технологии

- Python 3.10+
- Django 6
- Django REST Framework
- djangorestframework-simplejwt (JWT-аутентификация)
- django-cors-headers
- openpyxl (экспорт в Excel)
- SQLite

## Установка и запуск

### Шаг 1. Клонирование
git clone https://github.com/superdr0chun/diplom-django.git
cd diplom-django

### Шаг 2. Виртуальное окружение

Windows:
python -m venv venv
venv\Scripts\activate

macOS / Linux:
python3 -m venv venv
source venv/bin/activate

### Шаг 3. Установка зависимостей
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers openpyxl

### Шаг 4. Миграции
python manage.py makemigrations
python manage.py migrate

### Шаг 5. Создание преподавателя (опционально)
python manage.py shell
```python
from api.models import CustomUser
CustomUser.objects.create_user(username='teacher', email='teacher@test.com', password='123456', role='teacher')
```

### Шаг 6. Запуск сервера
python manage.py runserver

Сервер: http://127.0.0.1:8000

- Веб-интерфейс преподавателя: `/web/login/`
- Регистрация: `/web/register/`
- API: `/api/...`

## Структура API

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/api/register/` | Регистрация |
| POST | `/api/login/` | Авторизация (возвращает JWT) |
| POST | `/api/token/refresh/` | Обновление токена |
| GET | `/api/tests/` | Список доступных тестов |
| GET | `/api/tests/<id>/` | Детали теста |
| POST | `/api/tests/<id>/start/` | Начать тест (создаёт Result) |
| POST | `/api/tests/submit/` | Отправить ответы |
| GET | `/api/results/` | Список результатов |
| GET | `/api/results/<id>/` | Подробный разбор результата |

## Структура базы данных

- **CustomUser** — пользователи (логин, email, пароль, роль)
- **Test** — тесты (название, описание, дисциплина, время, попытки, настройки)
- **Question** — вопросы (тип, текст, баллы)
- **Answer** — варианты ответов с пометкой правильности
- **Result** — попытка прохождения (баллы, дата, переключения окон)
- **UserAnswer** — ответ студента на вопрос