include .env
export

develop:
	docker build --no-cache -t hide-server .
	docker-compose --env-file .env up -d

	docker exec hide-server sudo -u postgres psql -c "CREATE USER $(POSTGRES_USERNAME) WITH PASSWORD '$(POSTGRES_PASSWORD)';"
	docker exec hide-server sudo -u postgres psql -c "CREATE DATABASE $(POSTGRES_DATABASE);"
	docker compose restart hide-server

checkup:
	docker exec hide-server /bin/sh -c "cd /hide && python3 -W ignore -m coverage run -m unittest discover -s ./tests -p '*_tests.py'"
	docker exec hide-server /bin/sh -c "cd /hide && python3 -m coverage report --omit '/usr/lib/*,tests/*'"
	docker exec hide-server /bin/sh -c "flake8 --count --max-line-length=80 /hide"
