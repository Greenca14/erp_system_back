# Global ERP: Система управления обучением (Backend)
Бэкенд-часть приложения для планирования корпоративного обучения, расчета стоимости и мониторинга прогресса сотрудников.

# Технологический стек
Язык: Python 3.10+

Фреймворк: Django 5.x

API: Django REST Framework (DRF)

База данных: PostgreSQL (или SQLite для локальной разработки)

Интеграция: XML парсинг (Global ERP)

# Локальное развертывание
Подготовка окружения:

Клонирование репозитория
git clone <ссылка_на_репозиторий>
cd erp_system_back

Настройка виртуального окружения
python -m venv venv

Активация (Windows)
.\venv\Scripts\activate
Активация (Linux/Mac)
source venv/bin/activate

Установка зависимостей
pip install -r requirements.txt

# База данных и заполнение
Создание структуры таблиц
python manage.py migrate

Заполнение базы тестовыми данными (Курсы, Группы, Компании)
python manage.py seed_db

# Запуск сервера
python manage.py runserver

# Документация API (Swagger)
Для удобства интеграции с фронтендом настроен интерактивный Swagger. Там можно посмотреть все эндпоинты, форматы JSON и протестировать запросы.

Swagger UI: http://127.0.0.1:8000/api/v1/swagger/
Схема (JSON/YAML): http://127.0.0.1:8000/api/v1/




