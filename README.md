# Сервис проката автомобилей

Веб-приложение на **Django** для управления арендой автомобилей.  
Позволяет пользователям регистрироваться, просматривать каталог машин, бронировать авто, а администраторам — управлять автомобилями, локациями и заказами.

---

## Возможности

- Регистрация и авторизация пользователей  
- Просмотр списка доступных автомобилей  
- Детальная страница машины с фото и характеристиками  
- Бронирование автомобиля с указанием даты, места и срока аренды  
- Автоматический расчет стоимости аренды  
- Панель управления пользователем (мои заказы, история)  
- Админ-панель Django для управления пользователями, машинами и заказами  

---

## Технологии

- **Backend:** Django (Python 3.10+)  
- **Frontend:** HTML + Bootstrap  
- **База данных:** PostgreSQL  

---

## Установка и запуск

### 1. Клонирование проекта
```bash
git clone https://github.com/aivv73/diplom.git
cd diplom
````

### 2. Создание виртуального окружения

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка PostgreSQL

Создай базу данных и пользователя:

```sql
CREATE DATABASE car_rental;
CREATE USER car_user WITH PASSWORD 'yourpassword';
ALTER ROLE car_user SET client_encoding TO 'utf8';
ALTER ROLE car_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE car_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE car_rental TO car_user;
```

### 5. Конфигурация Django

В `diplom/settings.py` укажи подключение к базе:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'car_rental',
        'USER': 'car_user',
        'PASSWORD': 'yourpassword',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 6. Применение миграций

```bash
python manage.py migrate
```

### 7. Создание суперпользователя

```bash
python manage.py createsuperuser
```

### 8. Запуск сервера

```bash
python manage.py runserver
```

Открой в браузере: [http://127.0.0.1:8000](http://127.0.0.1:8000)
