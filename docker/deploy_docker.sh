#!/bin/bash
while [ -n "$1" ]
do
    case $1 in
        -d) MONGO_DIR=$2
        shift;;
        -l) LOG_DIR=$2
        shift;;
        *) echo "$1 is not an option"
        exit 1;;
    esac
    shift
done

if [ -z $MONGO_DIR ]
then
    echo "Option -d is required"
    exit 1
fi

if [ -z $LOG_DIR ]
then
    echo "Option -l is required"
    exit 1
fi

# установка прав на папку привязки
chmod -R 777 $MONGO_DIR
# удаление старого контейнера
docker rm -f bsc_fokin
# сборка образа
docker build -t bsc_fokin_image .
# запуск контейнера
docker run -p 8000:80 -v $MONGO_DIR:/data/db/ -v $LOG_DIR:/data/logs -d --name bsc_fokin -t bsc_fokin_image
