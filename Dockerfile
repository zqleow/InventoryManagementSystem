FROM mysql:latest

COPY init.sql /docker-entrypoint-initdb.d/

# Set environment variables
ENV MYSQL_DATABASE=inventory \
    MYSQL_USER=db_app_user \
    MYSQL_PASSWORD=admin_user \
    MYSQL_ROOT_PASSWORD=password

# Expose the MySQL port
EXPOSE 3306