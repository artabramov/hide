include .env
export

install:
	rm -rf ./hide-smokes
	mkdir ./hide-smokes
	git clone https://github.com/artabramov/hide-smokes.git ./hide-smokes
	docker rmi hide-smokes
	docker build --no-cache -t hide-smokes ./hide-smokes
	rm -rf ./hide-smokes

	docker build --no-cache -t hide .
	docker-compose --env-file .env up -d

	docker exec hide sudo -u postgres psql -c "CREATE USER $(POSTGRES_USERNAME) WITH PASSWORD '$(POSTGRES_PASSWORD)';"
	docker exec hide sudo -u postgres psql -c "CREATE DATABASE $(POSTGRES_DATABASE);"

	docker exec hide /bin/sh -c "echo \"listen_addresses = '*'\" >> /etc/postgresql/14/main/postgresql.conf"
	docker exec hide /bin/sh -c "sudo sed -i \"/^# IPv4 local connections:/a \host hide hide 0.0.0.0/0 md5\" /etc/postgresql/14/main/pg_hba.conf"
	docker exec hide /bin/sh -c "sudo sed -i \"/^# IPv4 local connections:/a \host hide hide 127.0.0.1/32 trust\" /etc/postgresql/14/main/pg_hba.conf"

	docker exec hide /bin/sh -c "echo \"bind 0.0.0.0\" >> /etc/redis/redis.conf"

	docker-compose restart hide
