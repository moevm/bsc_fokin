# bsc_fokin
Автоматизация работы преподавателя в курсах по программированию и информатике

## Инструкция по локальному запуску

* Активировать виртуальное окружение (в проекте используется интерпретатор Python 3.7)
```
virtualenv venv -p python3 && source venv/bin/activate
```
* Установить зависимости
```
pip install -r requirements.txt
```
* Запустить mongodb
```
service mongodb start
```
* Запустить сервер
```
python manage.py runserver -p 8000
```
* Перейти по адресу http://localhost:8000
