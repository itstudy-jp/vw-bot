run-dev:
	ENV_FILE=.env.dev docker-compose up --build

run-prod:
	ENV_FILE=.env.prod docker-compose up --build

down:
	docker compose down --rmi all --volumes