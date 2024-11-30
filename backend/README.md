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