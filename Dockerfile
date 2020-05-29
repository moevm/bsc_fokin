FROM ubuntu:18.04
WORKDIR /usr/bsc_fokin
RUN apt-get update && \
    apt-get install -y python3 python3-pip mongodb
RUN mkdir -p /data/logs/ && \
    mkdir /data/db/ && \
    mv /var/lib/mongodb /data/db/ && \
    ln -s /data/db/ /var/lib/mongodb && \
    chmod -R 777 /data/db/
COPY ./requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
EXPOSE 80
CMD ["./docker/run.sh"]
