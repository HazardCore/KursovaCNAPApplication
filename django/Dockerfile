FROM python:3.6
# FROM python:3.6
ENV DJANGO_SUPERUSER_PASSWORD root
ENV PYTHONUNBUFFERED=1
# COPY ./requirements.txt /requirements.txt

RUN apt-get update && apt-get install -y gcc libc-dev libreoffice gettext
# RUN pip install -r /requirements.txt
RUN pip install "Django==3.1.1" && pip install \
    django-admin-interface \
    django-colorfield \
    uwsgi spyne lxml zeep \
    django-import-export \
    django-simple-history \
    django-crispy-forms \
    django-cors-headers \
    pyOpenSSL \
    django-select2 \
    django-redis \
    django-celery-results \
    plotly \
    babel \
    django-celery-beat \
    -U drf-yasg \
    django-filter \
    backports-datetime-fromisoformat \
    influxdb-client \
    psycopg2 \
    typecheck-decorator \
    pandas \
    django-environ \
    django-cleanup \
    docxtpl \
    django-select2-admin-filters \
    typing \
    pillow \
    qrcode \
    fcm-django \
    django-redis-sentinel \
    django-advanced-filters \
    django-admin-rangefilter \
    django-tabbed-changeform-admin \
    django_admin_multiple_choice_list_filter \
    django-admin-autocomplete-filter \
    django-valueinlist-filter \
    django-modeladmin-reorder \
    pyjwt \
    django-silk \
    gunicorn


WORKDIR /app
COPY . /app

RUN mkdir -p /vol/web/media && \
    mkdir -p /vol/web/static && \
    mkdir -p /sock && \
    chmod +x /app/entrypoint.sh

# RUN adduser --disabled-password user && \
#     chown -R user:user /vol && \
#     chmod -R 755 /vol/web

# RUN chown -R user:user /app
# USER user

VOLUME /app
VOLUME /vol/web/media
VOLUME /vol/web/static
VOLUME /sock
EXPOSE 8000

CMD [ "bash", "/app/entrypoint.sh" ]