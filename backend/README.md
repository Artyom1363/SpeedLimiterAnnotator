# Video Annotation Backend API Documentation

## Running tests:
```
# собираем проект
docker-compose -f docker-compose.test.yml build --no-cache

# запускаем тесты
docker-compose -f docker-compose.test.yml run --rm test_backend pytest -v

# остановить все
docker-compose -f docker-compose.test.yml down -v
```


## Running service:

```
docker compose down -v && docker compose up --build
```


## To transfer to new server:

```
sudo cp nginx.conf /etc/nginx/sites-available/fastapi.conf
sudo ln -s /etc/nginx/sites-available/fastapi.conf /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo chown -R www-data:www-data /etc/nginx/sites-available/
sudo chown -R www-data:www-data /etc/nginx/sites-enabled/


# In backend directory:
mkdir -p ./uploads
chmod 777 ./uploads
```

