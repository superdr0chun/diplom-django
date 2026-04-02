REST API на Django REST Framework
-
Которое обеспечивает:

-Регистрацию новых пользователей

-Авторизацию существующих пользователей

-Управление сессиями

-Валидацию данных

API используется WPF-клиентом для аутентификации пользователей.

Системные требования
-
Windows 10 или Мак линукс разницы особой нету

Python 3.14

Минимум 2 ГБ RAM

Минимум 500 МБ на диске


Шаг 1
===
git clone https://github.com/superdr0chun/diplom-backend.git
cd diplom-backend


Шаг 2
===
виндос
python -m venv venv
venv\Scripts\activate

все остальные
python3 -m venv venv
source venv/bin/activate


Шаг 3
===
pip install django djangorestframework


Шаг 4
===
python manage.py makemigrations
python manage.py migrate


Шаг 5
===
python manage.py runserver

Сервер должен запуститься по http://127.0.0.1:8000 адресу
После этого переходим в WPF приложение и пытаемся регестрироваться/авторизоваться





По структуре
===
diplom-backend/
├── manage.py              
├── db.sqlite3             
├── venv/                  
├── api/                   
│   ├── __init__.py
│   ├── apps.py            
│   ├── models.py          
│   ├── views.py           
│   ├── serializers.py     
│   ├── urls.py            
│   └── tests.py          
├── myproject/             
│   ├── __init__.py
│   ├── settings.py        
│   ├── urls.py            
│   └── wsgi.py           
├── .gitignore             
└── README.md              
