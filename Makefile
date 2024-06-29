include .env
export

develop:
	docker build --no-cache -t hide-server .
	docker-compose --env-file .env up -d

	docker exec hide-server sudo -u postgres psql -c "CREATE USER $(POSTGRES_USERNAME) WITH PASSWORD '$(POSTGRES_PASSWORD)';"
	docker exec hide-server sudo -u postgres psql -c "CREATE DATABASE $(POSTGRES_DATABASE);"
	docker compose restart hide-server
