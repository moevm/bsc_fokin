# bsc_fokin
Автоматизация работы преподавателя в курсах по программированию и информатике

## Заполнение config.ini

* Создать приложение https://stepik.org/oauth2/applications/ с параметрами (stepic_oauth):
  + client type = confidential
  + authorization grant type = authorization-code

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

## Инструкция по запуску докера

* Запустить скрипт сборки образа и запуска контейнера с правами суперпользователя
```
sudo ./docker/deploy_docker.sh -d /полный/путь/к/папке/привязки/ -l /полный/путь/к/папке/с/логами/
```
Пример:
```
sudo ./docker/deploy_docker.sh -d /home/user/bsc/bsc_fokin/mongo -l /home/user/Programs/bsc/bsc_fokin/logs
```
* Перейти по адресу http://ip-адрес:8000
