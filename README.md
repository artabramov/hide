# hide-server

/etc/postgresql/14/main/postgresql.conf  
listen_addresses = '*'  
  
/etc/postgresql/14/main/pg_hba.conf  
host all all 0.0.0.0/0 md5  
  
/etc/redis/redis.conf  
bind 0.0.0.0  
