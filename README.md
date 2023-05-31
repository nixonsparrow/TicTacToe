# TIC TAC TOE
How simple game can be both challenging and satisfying.

Created with Flask technology and fully dockerized.

## Flask commands

#### create_db
**Drop** the database (if exists) and **create** a new one with a models' architecture.

#### seed_db
**Create** user with credentials stored in **SEED_USER** and **SEED_PASS**.
Defaults: "user" and "pass".

## Quick start locally

```
docker-compose build
docker-compose up -d

```
Additional useful commands
```
# RUN in DEBUG mode
python manage.py --app tictactoe run --debug

# Open shell with app's data
flask --app tictactoe shell
```

## Docker compose related commands

```
# Create database / recreate - BE CAREFUL WITH THIS COMMAND IN PRODUCTION!
docker-compose exec web python manage.py create_db

# Create User 
docker-compose exec web python manage.py seed_db

# Docker running opetations
docker-compose build
docker-compose build --no-cache
docker-compose up -d    # d makes in run in the background
docker-compose down       # remove existing containers       | CAREFUL IN PRODUCTION!
docker-compose down -v    # include volume of postgres data  | CAREFUL IN PRODUCTION!

# Docker check logs 
docker-compose logs

# Stop containers
docker-compose stop
docker stop tictactoe-web-1
docker stop tictactoe-db-1

# Start containers
docker-compose start
docker start tictactoe-web-1
docker start tictactoe-db-1
```
