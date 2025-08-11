build:
	docker build ./

run-dev:
	ENV_FILE=.env.dev docker compose up -d

run-prod:
	ENV_FILE=.env.prod docker compose up -d

start:
	docker compose start

stop:
	docker compose stop

down:
	docker compose down

delete:
	docker compose down --rmi all --volumes
