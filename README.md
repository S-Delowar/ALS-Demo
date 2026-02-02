### Run
#### Run docker-compose (vector db + redis)
```docker-compose up```
#### venv =>
```pip install -r requirements.txt```

```python manage.py makemigrations```

```python manage.py migrate```
### run celery
```celery -A core worker -l info --pool=solo```     #if windows

```celery -A core worker -l info```  #if linux/mac
### run server
```python manage.py runserver```
