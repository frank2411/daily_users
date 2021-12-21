# Daily Users


### Run the project

##### In order to run the project Docker and Docker-compose must be installed.

This chain of commands must be executed:

```shell
docker-compose up -d --build
docker-compose exec db psql -U postgres
```

Inside postgres shell run:

```SQL
postgres=# CREATE DATABASE daily_users;
postgres=# \q
```

Exit the shell and run:

```shell
docker-compose exec web flask init-db
```


Now you can go to http://localhost:5000/api/v1/docs and play with the APIs 


### Testing

##### In order to run tests a virtualenv and a "daily_users_test" database must be created.

The with the virtualenv activated simply run:

```shell
tox
```
