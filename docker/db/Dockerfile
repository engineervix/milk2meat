# pull official base image
FROM postgres:15.7

# run create.sql on init
ADD create.sql /docker-entrypoint-initdb.d/
