run-dev:
	ENV_FILE=.env.dev docker compose up -d --build

run-prod:
	ENV_FILE=.env.prod docker compose up -d --build

start:
	docker compose start

stop:
	docker compose stop

down:
	docker compose down --rmi all --volumes
