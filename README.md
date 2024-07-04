# hide-server

/etc/postgresql/14/main/postgresql.conf  
listen_addresses = '*'  
password_encryption = md5  
  
/etc/postgresql/14/main/pg_hba.conf  
host all all 0.0.0.0/0 md5
  
/etc/redis/redis.conf  
bind 0.0.0.0  

grafana dashboards  
11074 (Node Exporter)  
12485 (PostgreSQL exporter)  
11835 (Redis Exporter)  

export DATA_SOURCE_NAME="postgresql://hide:he7w2rLY4Y8pFk2u@127.0.0.1:5432/hide?sslmode=disable" 
