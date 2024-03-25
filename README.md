# Yatube
Learning project. Yatube is a simple social network with basic functionality. Application offers following functions: creating different types of users, adding and modifying of postst, commenting postst of other users, subscriptions system and adding posts to user favorits section. Posts could also be added in various groups, which are predefined by administrator. Fronend was developed using HTML, Bootstrap and JavaScript. 

# Technology Stack
Python, Django, SQLite, Bootstrap.

# Launching
Create Python environment.
```
python3.7 -m venv venv
```
Start Python environment.
```
source venv/bin/activate
```
Install dependencies.
```
pip install -r requirements.txt
```
Perform migrations.
```
python3 manage.py migrate
```
Create superuser.
```
python3 manage.py createsuperuser
```
Run the project.
```
python3 manage.py runserver
```
**Project is available on:**
http://127.0.0.1:8000/
http://127.0.0.1:8000/admin/

# Авторы
[IPfa](https://github.com/IPfa)