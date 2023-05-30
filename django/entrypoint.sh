#!/bin/bash

set -e

FILE="/vol/status.init"

POSITIONAL=()
while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
    -u|--uwsgi)
      UWSGI=1
      shift
      ;;
    *)
      shift
      ;;
  esac
done

cp -r ./media/admin-interface /vol/web/media/

python manage.py collectstatic --noinput
python manage.py makemigrations
python manage.py migrate

if [ ! -f "$FILE" ];
then
    python manage.py loaddata init.json
    touch $FILE
fi

python manage.py runserver 0.0.0.0:8000