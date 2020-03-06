# apache-logs


# usage
```
git clone git@github.com:Ravillatypov/apache-logs.git
docker-compose up -d --build
docker exec -it apache-logs_app_1 python manage.py parse_log http://www.almhuette-raith.at/apache-log/access.log
curl -H "Content-Type: application/json" http://127.0.0.1:8000/api/v1/logs
```
