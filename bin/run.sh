#!/usr/bin/env bash
export APP_ENV="dev"

function start () {
    source .venv/bin/activate
    #gunicorn -b 127.0.0.1:5000 --reload app.main:application
    #uwsgi --http 0.0.0.0:5000 --chdir /home/hydrogen/Documents/Work/sigma/kidssy/sourceCode/Kidssy/course --http-processes 2 --gevent 100 --workers 2 --master --max-requests 300 --thunder-lock --listen 100 --post-buffering 4192 --module app.main:application
    #uwsgi --http 0.0.0.0:5000 --gevent 200 --processes 5 --master --max-requests 300 --thunder-lock --listen 4096 --post-buffering 4192 --module app.main:application
    #uwsgi --http 0.0.0.0:5000 --enable-threads --processes 5 --threads 8 --master --max-requests 300 --thunder-lock --listen 4096 --post-buffering 4192 --module app.main:application
    /home/anhdt/falcon-REST/.venv/bin/uwsgi -c /home/anhdt/falcon-REST/bin/uwsgi.ini
}

function stop () {
    #ps -ef | grep gunicorn | awk '{print $2}' | xargs kill -9
    ps -ef | grep uwsgi | awk '{print $2}' | xargs kill -9
}

case "$1" in
    start)
        start
        ;;
    stop)
        stop
        ;;
    *)
    echo "Usage: run.sh {start|stop}"
    exit 1
esac
