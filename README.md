# Yatube

Небольшой сайт с базовым функционалам. Возможность регистрации пользователей разных типов. Хранение данных. Каждый пользователь может вести дневник. Пользователи могут просматривать дневники друг друга. Красивое оформление с использованием разных шрифтов.

# Стек Технологий
Python, Django, SQLite, Bootstrap.

# Запуск
Развернуть виртуальное окружение.
```
python3.7 -m venv venv
```
Запустить виртуальное окружение.
```
source venv/bin/activate
```
Установить зависимости.
```
pip install -r requirements.txt
```
Перейти в папку Yatube и запустить проект.
```
python3 manage.py runserver
```
Команды для сбора статики, выполнения миграций и создания суперпользователя.
```
python3 manage.py migrate
```
```
python3 manage.py collectstatic
```
```
python3 manage.py createsuperuser
```
**Проект доступен по адресу:**
http://127.0.0.1/

# Авторы
[IPfa](https://github.com/IPfa)