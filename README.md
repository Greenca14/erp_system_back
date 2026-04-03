# Global ERP: Система управления обучением (Backend)
Бэкенд-часть приложения для планирования корпоративного обучения, расчета стоимости и мониторинга прогресса сотрудников.

# Технологический стек
Язык: Python 3.10+

Фреймворк: Django 5.x

API: Django REST Framework (DRF)

База данных: PostgreSQL (или SQLite для локальной разработки)

Интеграция: XML парсинг (Global ERP)

# Локальное развертывание
Клонирование репозитория:

Bash

git clone <ссылка_на_ваш_репозиторий>
cd erp_system_back
Настройка виртуального окружения:

Bash

python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
Установка зависимостей:

Bash

pip install -r requirements.txt
(Если файла еще нет, установи вручную: pip install django djangorestframework django-cors-headers)

Миграции и База данных:

Bash

python manage.py makemigrations
python manage.py migrate
Создание администратора:

Bash

python manage.py createsuperuser
Запуск сервера:

Bash

python manage.py runserver
API будет доступно по адресу: http://127.0.0.1:8000/
