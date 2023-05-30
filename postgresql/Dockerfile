FROM postgres:10-alpine

ENV POSTGRES_USER postgres
ENV POSTGRES_PASSWORD passw0rd

COPY init.sql /docker-entrypoint-initdb.d/

RUN chmod 0777 /docker-entrypoint-initdb.d/init.sql

EXPOSE 5432

# pg_dump -h localhost -U devpg -F c -f /tmp/init_settings.tar.gz \
# -t admin_interface_theme default_db


# pg_restore -h localhost -U devpg -W -F c -d default_db /app/init_settings.tar.gz