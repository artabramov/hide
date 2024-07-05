include .env
export

install:
	docker build --no-cache -t hide-server .
	docker-compose --env-file .env up -d

	docker exec hide-server sudo -u postgres psql -c "CREATE USER $(POSTGRES_USERNAME) WITH PASSWORD '$(POSTGRES_PASSWORD)';"
	docker exec hide-server sudo -u postgres psql -c "CREATE DATABASE $(POSTGRES_DATABASE);"

	docker exec hide-server /bin/sh -c "echo \"listen_addresses = '*'\" >> /etc/postgresql/14/main/postgresql.conf"
	sudo sed -i "/^# IPv4 local connections:/a \host hide hide 0.0.0.0/0 md5" /etc/postgresql/14/main/pg_hba.conf
	sudo sed -i "/^# IPv4 local connections:/a \host hide metrics 127.0.0.1/32 trust" /etc/postgresql/14/main/pg_hba.conf

	docker exec hide-server /bin/sh -c "echo \"bind 0.0.0.0\" >> /etc/redis/redis.conf"

	docker compose restart hide-server

	docker exec hide-server /bin/sh -c "cd /hide && python3 -W ignore -m coverage run -m unittest discover -s ./tests -p '*_tests.py'"
	docker exec hide-server /bin/sh -c "cd /hide && python3 -m coverage report --omit '/usr/lib/*,tests/*'"
	docker exec hide-server /bin/sh -c "flake8 --count --max-line-length=80 /hide"
