# TIC TAC TOE
How simple game can be both challenging and satisfying.

Created with Flask technology and fully dockerized.

## Flask commands

#### create_db
**Drop** the database (if exists) and **create** a new one with a models' architecture.

## Quick start: dockerize development
In the root folder, copy `.env.example` file and name the new file `.env.dev`.

In the services/web/tictactoe folder copy `config_example.py` file and name the new file `config.py`.

After that stay in the root folder and use following commands: 
```
# give permissions to your entrypoint.sh file
chmod +x services/web/entrypoint.sh

# build and run
docker-compose build
docker-compose up -d

# delete if not needed anymore
docker-compose down -v
```
To use the application visit http://localhost5000 in your browser.

#### Additional useful commands
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

# Docker running opetations
docker-compose build
docker-compose build --no-cache
docker-compose up -d      # d makes in run in the background
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

## Production
Basically it's the same way as dev server, but you need to use different files:
- create .env.prod for environment variables:
  - `APP_FOLDER=/home/app/web`
  - `DATABASE_URL= <URL with proper database data>`
- create .env.prod.db for database environment variables:
  - `POSTGRES_USER= <database user>`
  - `POSTGRES_PASSWORD= <database password>`
  - `POSTGRES_DB= <database name>`

And most importantly, to every docker command add the "-f" flag: `-f docker-compose.prod.yml` 
to point the file that want to use to build images and run. Example:
```
docker-compose -f docker-compose.prod.yml build
```
If you need to create database (if you get Internal error at homepage):
```
docker-compose -f docker-compose.prod.yml exec web python manage.py create_db
```

## Game and session description
#### Game info
Tic-tac-toe is a simple 2-player game with two signs and 9 fields arranged in a 3x3 grid.
Main goal is to place 3 signs in a row, column or in a diagonal. Players take turns.

#### Session info
In our application you have 10 coins in each created game session. To start a game within
the session you need to spend 3 coins. If you win, you get 4 coins, so there is a possibility
to have infinite games in a one session.